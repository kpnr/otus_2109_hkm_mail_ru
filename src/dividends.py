"""Get & save MOEX shares dividends"""
from urllib.request import urlopen
from pprint import pp
import re
from dataclasses import dataclass
import xml.etree.ElementTree as ET
from datetime import date


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
        shortname: str
        status: str
        secname: str
        isin: str
        latname: str
        regnumber: str
        listlevel: int

    @dataclass
    class Dividend:
        """Dividend info"""
        secid: str
        isin: str
        registryclosedate: date
        value: float
        currencyid: str

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
        rv = [self.Security(**({k.lower(): v for k, v in row.attrib.items() if k.lower() in attrs}))
              for row in dom.iterfind('./data[@id="securities"]/rows/')]
        return rv

    def dividends(self, security: Security) -> list[Dividend]:
        """Get Divident for security"""
        dom = self._xml_load(f"securities/{security.secid}/dividends.xml?lang={self.LANG}")
        rv = [self.Dividend(**x.attrib) for x in dom.iterfind('./data[@id="dividends"]/rows/')]
        return rv


moex = MOEX()
engine = next((x for x in moex.engines() if x.name == 'stock'))
market = next((x for x in moex.markets(engine) if x.name == 'shares'))
board = next((x for x in moex.boards(market) if x.is_traded == '1' and x.boardid == 'TQBR'))
securities = moex.securities(board)
dividends = moex.dividends(securities[111])
pp(board)
