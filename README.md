
Отус "Архитектура и шаблоны проектирования"
============================================

Урок 3
--------

**Домашнее задание** Движение игровых объектов по полю.

**Цель:** Выработка навыка применения SOLID принципов на примере игры "Танки".

В результате выполнения ДЗ будет получен код, отвечающий за движение объектов
по игровому полю, устойчивый к появлению новых игровых объектов
и дополнительных ограничений, накладываемых на это движение.

Описание игры по [ссылке](https://docs.google.com/document/d/19QXXaUEAIMkYsZZceSCkZ8jkkryMPpqJUotwV3GGIgQ/edit?usp=sharing)

Реализовать движение объектов на игровом поле в рамках подсистемы Игровой сервер.

Урок 4
--------

Многопоточное выполнение команд.

Предположим, что у нас есть набор команд, которые необходимо выполнить.
Выполнение команд организуем в несколько потоков. Для этого будем считать,
что у каждого потока есть своя потокобезопасная очередь.
Для того, чтобы выполнить команду, ее необходимо добавить в очередь.
Поток читает очередную команду из очереди и выполняет ее.
Если выполнение команды прерывается выброшенным исключением,
 то поток должен отловить его и продолжить работу.
Если сообщений нет в очереди, то поток засыпает до тех пор, пока очередь пуста.

Урок 13
---------
Предположим, что у нас уже написаны команды MoveCommand и RotateCommand. 
Теперь возникло новое требование: пользователи в игре могут устанавливать 
правило - во время движение расходуется топливо, двигаться можно 
только при наличии топлива.

Реализовать новую возможность можно введя две новые команды.
CheckFuelCommand и BurnFuelCommand.

CheckFuelCommand проверяет, что топлива достаточно, если нет, то выбрасывает исключение CommandException.

BurnFuelCommand уменьшает количество топлива на скорость расхода топлива.

После этого мы можем три команды выстроить в цепочку.
CheckFuelCommand MoveCommand BurnFuelCommand

Чтобы это было прозрачно для пользователя реализуем Макрокоманду - специальную 
разновидность команды, которая в конструкторе  принимает массив команда,
а методе execute их все последовательно выполняет.

При повороте движущегося объекта меняется вектор мгновенной скорости.
Напишите команду, которая модифицирует вектор мгновенной скорости, в случае поворота.
Постройте цепочку команд для поворота.

1. Реализовать класс CheckFuelComamnd и тесты к нему.

2. Реализовать класс BurnFuelCommand и тесты к нему.

3. Реализовать простейшую макрокоманду и тесты к ней. Здесь простейшая - это значит,
   что при выбросе исключения вся последовательность команд приостанавливает свое
   выполнение, а макрокоманда выбрасывает CommandException.

4. Реализовать команду движения по прямой с расходом топлива, используя команды с предыдущих шагов.

5. Реализовать команду для модификации вектора мгновенной скорости при повороте.
   Необходимо учесть, что не каждый разворачивающийся объект движется.
6. Реализовать команду поворота, которая еще и меняет вектор мгновенной скорости, если есть.


# Урок 14


Реализация IoC контейнера

**Цель:** Реализовать IoC контейнер, устойчивый к изменению требований.

**В результате** выполнения домашнего задания Вы получите IoC, который можно будет
использовать в своих проектах.

В игре танки есть набор операций над игровыми объектами: движение по прямой,
поворот, выстрел. При этом содержание этих команд может отличаться для разных
игр, в зависимости от того, какие правила игры были выбраны пользователями.

Например, пользователи могут ограничить запас ход каждого танка некоторым
количеством топлива, а другой игре запретить поворачиваться танкам
по часовой стрелке и т.д.

IoC может помочь в этом случае, скрыв детали в стратегии разрешения зависимости.

Например, IoC.Resolve("двигаться прямо", obj); возвращает команду, которая чаще
всего является макрокомандой и осуществляет один шаг движения по прямой.

## Реализовать IoC контейнер, который:

1. Разрешает зависимости с помощью метода, со следующей сигнатурой:
    T IoC.Resolve(string key, params object[] args);

1. Регистрация зависимостей также происходит с помощью метода Resolve
    IoC.Resolve("IoC.Register", "aaa", (args) => new A()).Execute();

    Зависимости можно регистрировать в разных "скоупах"
    IoC.Resolve("Scopes.New", "scopeId").Execute();
    IoC.Resolve("Scopes.Current", "scopeId").Exceute();

Указание: Для работы со скоупами используйте ThreadLocal контейнер.

## Критерии оценки:

1. Интерфейс IoC устойчив к изменению требований.
    Оценка: 0 - 5 баллов (0 - совсем не устойчив,
    5 - преподаватель не смог построить ни одного контрпримера)

1. IoC предоставляет ровно один метод для всех операций. 3 балла

1. IoC предоставляет работу со скоупами для предотвращения сильной связности. 5 баллов.

1. Реализованы модульные тесты. 5 баллов

1. Реализованы многопоточные тесты. 2 балла
