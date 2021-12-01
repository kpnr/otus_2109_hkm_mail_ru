"""
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

1. Реализовать класс BurnFuelCommand и тесты к нему.

1. Реализовать простейшую макрокоманду и тесты к ней. Здесь простейшая - это значит,
   что при выбросе исключения вся последовательность команд приостанавливает свое
   выполнение, а макрокоманда выбрасывает CommandException.

1. Реализовать команду движения по прямой с расходом топлива, используя команды с предыдущих шагов.

1. Реализовать команду для модификации вектора мгновенной скорости при повороте.
   Необходимо учесть, что не каждый разворачивающийся объект движется.
1. Реализовать команду поворота, которая еще и меняет вектор мгновенной скорости, если есть.
"""