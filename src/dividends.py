"""Get & save MOEX shares dividends"""
import re
import sqlite3
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable, Optional
from urllib.parse import urlencode
from urllib.request import urlopen

DB_NAME = './dividends.db3'

"""
Some SQL for optimal tickers

with div(fixdate, ticker, value, period) as (
    select divd.fixdate fixdate, divd.ticker ticker, divd.value value, divd.fixdate - lag(divd.fixdate) over () fixdate_prev
    from tDividends divd
    order by divd.ticker, divd.fixdate),
    div_day_return(fixdate, ticker, value, period, avg_rate, avg_day_return) as(
        select divd.fixdate, divd.ticker, divd.value, divd.period
             , avg(rate.rate)
             , divd.value/(avg(rate.rate) * divd.period) avg_day_return
        from div divd
          left join tDayRates rate on rate.ticker = divd.ticker
        where divd.period is not null
          and rate.date_ between divd.fixdate-divd.period and divd.fixdate
        group by divd.ticker, divd.fixdate)
select day_ret.ticker
      , sum(day_ret.avg_day_return * day_ret.period)/sum(day_ret.period) per_day_avg
      , sum(day_ret.avg_day_return * day_ret.period) total_ret
      , min(day_ret.avg_day_return) per_day_min, max(day_ret.avg_day_return) per_day_max
from div_day_return day_ret
where julianday('now') - julianday('1970-01-01') - 5*365 < day_ret.fixdate
group by day_ret.ticker
order by 2 desc;

select div.ticker, date('1970-01-01', ''||div.fixdate||' days'), div.value
from tDividends div
where div.ticker in ('GAZP', 'TRMK', 'PHOR')
order by div.ticker, div.fixdate desc
"""
class MOEX:
    """MOEX API handling class"""
    API_ROOT = r"http://iss.moex.com/iss"
    LANG = "ru"
    _re_content_type_charset = re.compile(r'charset=(?P<set>.+?)(\s|;|$)')

    @dataclass
    class Engine:
        """Engine short info"""
        id: int
        name: str
        title: str

    @dataclass
    class Market:
        """Market short info"""
        id: int
        name: str
        title: str
        engine: str

    @dataclass
    class Board:
        """Board short info"""
        id: int
        board_group_id: int
        boardid: str
        title: str
        is_traded: bool
        market: str
        engine: str

    @dataclass
    class Security:
        """Security info"""
        secid: str
        boardid: str
        market: str
        engine: str
        shortname: str
        status: str
        secname: str
        isin: str
        latname: str
        regnumber: str
        listlevel: int

    @dataclass
    class SecurityRateDaily:
        """Security trading rate info"""
        secid: str
        boardid: str
        open: float
        high: float
        low: float
        close: float
        volume: float
        currencyid: str
        tradedate: date

        def __post_init__(self):
            for float_name in ('open', 'high', 'low', 'close', 'volume',):
                v = getattr(self, float_name)
                if not isinstance(v, float):
                    setattr(self, float_name, float(v))
            if isinstance(self.tradedate, str):
                self.tradedate = date(*(int(x) for x in self.tradedate.split('-')))

    @dataclass
    class Dividend:
        """Dividend info"""
        secid: str
        isin: str
        registryclosedate: date
        value: float
        currencyid: str

        def __post_init__(self):
            if isinstance(self.registryclosedate, str):
                self.registryclosedate = date(*(int(x) for x in self.registryclosedate.split('-')))
            if isinstance(self.value, str):
                self.value = float(self.value)

    def _xml_load(self, url: str) -> ET:
        """Load and parse XML from URL"""
        with urlopen(f"{self.API_ROOT}/{url}") as resp:
            assert resp.status == 200
            dom = ET.parse(resp)
        return dom

    def engines(self) -> list[Engine]:
        """Get Engines list"""
        dom = self._xml_load(f"engines?lang={self.LANG}")
        rv = [self.Engine(**row.attrib) for row in dom.iterfind('./data[@id="engines"]/rows/')]
        return rv

    def markets(self, engine: Engine) -> list[Market]:
        """Get Markets list for Engine"""
        engine_name = engine.name
        dom = self._xml_load(f"engines/{engine_name}/markets.xml?lang={self.LANG}")
        rv = [self.Market(**({'engine': engine_name} | {k.lower(): v for k, v in row.attrib.items()}))
              for row in dom.iterfind('./data[@id="markets"]/rows/')]
        return rv

    def boards(self, market: Market) -> list[Board]:
        """Get boards list for Market"""
        engine = market.engine
        dom = self._xml_load(f"engines/{engine}/markets/{market.name}/boards.xml?lang={self.LANG}")
        rv = [self.Board(**({'engine': engine, 'market': market.name} | row.attrib))
              for row in dom.iterfind('./data[@id="boards"]/rows/')]
        return rv

    def securities(self, board: Board) -> list[Security]:
        """Get Securities traded on board"""
        dom = self._xml_load(f"engines/{board.engine}/markets/{board.market}/boards/{board.boardid}/securities.xml"
                             f"?lang={self.LANG}")
        attrs = set(self.Security.__dataclass_fields__.keys())
        rv = [self.Security(engine=board.engine, market=board.market,
                            **({k.lower(): v for k, v in row.attrib.items() if k.lower() in attrs}))
              for row in dom.iterfind('./data[@id="securities"]/rows/')]
        return rv

    def dividends(self, security: Security) -> list[Dividend]:
        """Get Divident for security"""
        dom = self._xml_load(f"securities/{security.secid}/dividends.xml?lang={self.LANG}")
        rv = [self.Dividend(**x.attrib) for x in dom.iterfind('./data[@id="dividends"]/rows/')]
        return rv

    def rates_daily(self, security: Security, from_: Optional[date] = None, to_: Optional[date] = None) -> list[
        SecurityRateDaily]:
        """Get daily security rates"""

        def cursor_advance():
            """Advance result by current chunk and update cursor position"""
            nonlocal rv, index, total, pagesize
            for row in dom.iterfind('./data[@id="history"]/rows/'):
                a = row.attrib
                if a['BOARDID'] != security.boardid or any(not a[x] for x in ('OPEN', 'CLOSE')):
                    continue
                rv.append(self.SecurityRateDaily(
                        **({k.lower(): v for k, v
                            in a.items()
                            if k.lower() in attrs}))
                        )
            cursor_dom = dom.find('./data[@id="history.cursor"]/rows/row')
            index, total, pagesize = [int(cursor_dom.attrib[n]) for n in ('INDEX', 'TOTAL', 'PAGESIZE')]
            return

        rv, index, pagesize, total = ([], 0, 0, 1)
        attrs = set(self.SecurityRateDaily.__dataclass_fields__.keys())
        url = (f"history/engines/{security.engine}/markets/{security.market}/securities/"
               f"{security.secid}.xml")
        url_params = {'start': 0}
        if from_ is not None:
            url_params['from'] = from_.strftime('%Y-%m-%d')
        if to_ is not None:
            url_params['to'] = to_.strftime('%Y-%m-%d')
        while index + pagesize < total:
            url_params['start'] = index + pagesize
            dom = self._xml_load(f'{url}?{urlencode(url_params)}')
            cursor_advance()
        return rv


def main():
    """Main function"""

    def db_init() -> sqlite3.Connection:
        """Open and init db-connection"""
        rv = sqlite3.connect(DB_NAME, timeout=30.0)
        for x in ('PRAGMA page_size = 4096;',
                  'PRAGMA encoding = "UTF-8";',
                  'PRAGMA foreign_keys = ON;',
                  'PRAGMA journal_mode = WAL;',
                  'PRAGMA recursive_triggers = ON;',
                  'PRAGMA auto_vacuum = 2;',
                  'PRAGMA incremental_vacuum(1024);',
                  """
                  CREATE TABLE IF NOT EXISTS tDividends (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  ticker VARCHAR(32),
                  name VARCHAR(128),
                  fixdate INTEGER,
                  value DOUBLE PRECISION,
                  currency VARCHAR(31),
                  UNIQUE (ticker, fixdate) ON CONFLICT REPLACE)""",
                  """
                  CREATE TABLE IF NOT EXISTS tDayRates (
                  id INTEGER PRIMARY KEY autoincrement,
                  ticker VARCHAR(16),
                  exchange VARCHAR(10),
                  date_ INTEGER,
                  rate DOUBLE PRECISION,
                  currency VARCHAR(16),
                  id_dividend INTEGER references tDividends(id),
                  UNIQUE (ticker, exchange, date_) ON CONFLICT REPLACE)
                  """,
                  '''
                  CREATE TABLE IF NOT EXISTS tTickers(
                  exchange VARCHAR(10) NOT NULL, 
                  ticker VARCHAR(16) NOT NULL, 
                  asset VARCHAR(10) NOT NULL,
                  base VARCHAR(10) NOT NULL,
                  PRIMARY KEY (exchange, ticker) ON CONFLICT REPLACE)'''
                  ):
            rv.execute(x)
        rv.row_factory = sqlite3.Row
        return rv

    def dividends_save(db: sqlite3.Connection, securities: Iterable[MOEX.Security]):
        """Load divinends into db"""
        date_base = date(1970, 1, 1)
        for security in securities:
            print(f"Dividend: {security.secid}")
            dividends = moex.dividends(security)
            for dividend in dividends:
                db.execute("""
                    INSERT INTO tDividends(ticker, name, fixdate, value, currency)
                    VALUES(:ticker,
                      :name,
                      :day_no,
                      :value,
                      :currency)""",
                           dict(ticker=dividend.secid,
                                name=security.secname,
                                day_no=(dividend.registryclosedate - date_base).days,
                                value=dividend.value,
                                currency=dividend.currencyid,
                                ))
        db.commit()

    def tickers_save(db: sqlite3.Connection, securities: Iterable[MOEX.Security]):
        """Load save securities into db"""
        for security in securities:
            db.execute("""
                INSERT OR REPLACE INTO tTickers(exchange, ticker, asset, base)
                VALUES(:exchange,
                  :ticker,
                  :name,
                  :board)""",
                       dict(exchange='MOEX',
                            ticker=security.secid,
                            name=security.secname,
                            board=security.boardid))
        db.commit()

    def security_rates_save(db: sqlite3.Connection, security: MOEX.Security):
        """Save trade rates for security"""
        date_base = date(1970, 1, 1)
        print(f"Reading rates for {security.secid}")
        start_day = db.execute(
                "select max(d.date_) start_day from tDayRates d where d.ticker=:ticker",
                {"ticker": security.secid}).fetchone()['start_day']
        start_date = None
        if start_day is not None:
            start_date = date_base + timedelta(days=start_day)
        for rate in moex.rates_daily(security, from_=start_date):
            db.execute(
                    """
                    INSERT OR REPLACE INTO tDayRates(exchange, ticker, date_, rate, currency, id_dividend)
                    VALUES(:exchange,
                      :ticker,
                      :day_no,
                      :rate,
                      :currency,
                      null)""",
                    dict(exchange=rate.boardid,
                         ticker=rate.secid,
                         day_no=(rate.tradedate - date_base).days,
                         rate=0.5 * (rate.open + rate.close),
                         currency=rate.currencyid,
                         ))
        db.commit()

    db = db_init()
    moex = MOEX()
    engine = next((x for x in moex.engines() if x.name == 'stock'))
    market = next((x for x in moex.markets(engine) if x.name == 'shares'))
    board = next((x for x in moex.boards(market) if x.is_traded == '1' and x.boardid == 'TQBR'))
    securities = moex.securities(board)
    tickers_save(db, securities)
    # uncomment to (re-)load dividends
    # dividends_save(db, securities)

    for security in securities:
        cur = db.execute("select 1 from tDividends d where d.ticker=:ticker", {"ticker": security.secid})
        if cur.fetchone():
            security_rates_save(db, security)
    db.close()


if __name__ == '__main__':
    main()
    exit(0)
