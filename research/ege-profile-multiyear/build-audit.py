"""Hand-reviewed task/method map, official FIPI 2019–2027 sample. Does not edit book."""
from pathlib import Path
import json,re,csv,hashlib,collections,copy
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'research/ege-profile-multiyear'
bookpath=ROOT/'sources/book/book-data.json'; book=json.loads(bookpath.read_text()); chapters={c['id']:(i,c) for i,c in enumerate(book,1)}
alltasks={t['uid']:(i,c['id'],j,t) for i,c in enumerate(book,1) for j,t in enumerate(c['tasks'],1)}
methods={}
def M(key,description,cids,sections,examples,tasks,status='covered-method',gap=''):
 methods[key]={'description':description,'chapter_ids':cids.split(','),'section_searches':sections.split('|') if sections else [],'example_refs':[{'chapter_id':v.split(':')[0],'ordinal':int(v.split(':')[1]),'uid_kind':'audit-derived; source example has no independent UID'} for v in examples.split(',') if v],'task_uids':tasks.split(',') if tasks else [],'status':status,'gap':gap}
M('time','Вычисление длительности через полночь и перевод единиц','exam-measurements,c01','Величины и единицы','exam-measurements:1','exam-measurements.4,c01.1')
M('ceil','Минимальная целая закупка: округление частного вверх','exam-measurements','Округление и направленное округление','exam-measurements:2','exam-measurements.8,exam-measurements.17')
M('percent','Скидка как умножение на долю оставшейся цены','c04,exam-models','Проценты','exam-models:4','exam-models.18,exam-models.19')
M('floor-index','Нумерация предметов блоками: остаток и целая часть','exam-measurements,c21','Округление|Деление с остатком','exam-measurements:2','exam-measurements.9,c21.1')
M('data-read','Чтение точек, диапазонов и порогов на графике/диаграмме','exam-measurements,statistics','Проценты, масштаб и чтение данных|Диаграммы','statistics:1','exam-measurements.19,exam-statistics.1,exam-statistics.2', 'partial','G4: мало задач, где ответ надо снять именно с рисунка, а не с выписанных чисел')
M('grid-area','Площадь на клетчатой бумаге: основание/высота или координаты','plane-geometry,c18','Площади','c18:1','plane-geometry.4,plane-geometry.17')
M('midline','Средняя линия треугольника/трапеции; подобие и части средней линии','exam-plane,plane-geometry','Подобие|Четырёхугольники','exam-plane:4','exam-plane.15,exam-plane.16,plane-geometry.5')
M('prob-classic','Равновероятные исходы, доля благоприятных, симметрия выбора','probability','Классическая','probability:1','probability.2,probability.3,probability.17')
M('prob-nested','Разность вероятностей вложенных событий; границы дискретного интервала','probability','Следствия аксиом вероятности','probability:2','probability.4,probability.18')
M('prob-repeat','Независимые испытания; заданная последовательность или дополнение','probability','Независимость и повторные испытания','probability:1','probability.13,probability.14,probability.15,probability.16')
M('prob-draw','Выбор без возвращения: условное умножение или сочетания','probability,c10','Условная вероятность','probability:1','probability.8,probability.9,probability.17')
M('prob-cond','Условная вероятность с новым конечным пространством исходов','probability,c10','Условная вероятность','probability:1','probability.7,probability.23')
M('prob-total','Полная вероятность по причинам/группам','probability','Полная вероятность','probability:2','probability.11,probability.12')
M('prob-union','Включение-исключение, дополнение пересечения; независимость не предполагается','probability','Следствия аксиом вероятности','probability:2','probability.4,probability.6')
M('expectation','Математическое ожидание по таблице распределения/частот','random-variables','Математическое ожидание','random-variables:1','random-variables.3,exam-final-random-variables.1')
M('eq-exp','Показательное уравнение: приведение к общему основанию','exam-exponential,c14-exponential','Показательные','exam-exponential:1','exam-exponential.1,exam-exponential.2')
M('eq-rad','Иррациональное уравнение: ОДЗ, знак, равносильное возведение в степень','exam-rational','Иррациональные','exam-rational:4','exam-rational.6,exam-rational.7,exam-rational.8')
M('eq-log','Логарифмическое уравнение через определение, с ОДЗ','exam-exponential,c14-exponential','Логарифмические','exam-exponential:4','exam-exponential.10,exam-exponential.11')
M('eq-quad','Квадратное уравнение и отбор требуемого корня','c11,exam-rational','Квадратные','exam-rational:2','exam-rational.10,c11.4')
M('circle-angle','Вписанные/центральные углы, вписанный четырёхугольник','plane-geometry,exam-plane','Окружности','exam-plane:5','plane-geometry.11,exam-plane.23,exam-plane.24')
M('triangle-angle','Сумма углов, внешний угол, равнобедренность, биссектриса','plane-geometry,exam-plane','От условия к признаку','exam-plane:1','plane-geometry.1,plane-geometry.3,exam-plane.3')
M('right-median','Высота и медиана прямоугольного треугольника: угол через подобие/равные радиусы','exam-plane,plane-geometry','Подобие','exam-plane:2','exam-plane.7,plane-geometry.22')
M('parallelogram','Площади параллелограмма, треугольников и вычитаемой трапеции','plane-geometry,exam-plane','Четырёхугольники','exam-plane:4','plane-geometry.17,plane-geometry.18,exam-plane.17')
M('rhombus-angle','Биссектрисы углов ромба и сумма соседних углов','exam-plane','Четырёхугольники','exam-plane:4','exam-plane.20,exam-plane.21')
M('tangential-quad','Равные касательные: суммы противоположных сторон описанного четырёхугольника','exam-plane','Окружности','exam-plane:5','exam-plane.26,exam-plane.27')
M('vector-dot','Координаты направленного вектора и скалярное произведение','c18','Координаты, длина и скалярное произведение','c18:1','c18.3,c18.4')
M('vector-length','Сложение/масштабирование координат и евклидова длина','c18','Координаты, длина и скалярное произведение','c18:1','c18.1,c18.2,c18.4')
M('derivative-sign','Знак производной по графику функции/производной','c20','Графики функции и её производной','c20:5','exam-calculus.11,exam-calculus.12','partial','G4: теория верна; упражнения почти не требуют самостоятельного чтения нарисованной кривой')
M('tangent-slope','Производная как наклон касательной: приращение y / приращение x','c20','Графики функции и её производной','c20:5','c20.9,exam-calculus.6,exam-calculus.12','partial','G4: добавить касательные на координатной сетке с численным считыванием наклона')
M('derivative-extremum','По графику f\' считать смены знака с нужным направлением','c20','Исследование функции с помощью производной|Графики функции','c20:5','exam-calculus.10,exam-calculus.11','partial','G4: есть словесные задачи на знаки, мало независимой графической практики')
M('cylinder-ratio','Цилиндр: сохранение объёма, отношение радиусов/высот','solid-geometry','Многогранники и тела вращения','solid-geometry:1','solid-geometry.4,exam-final-solid-geometry.1')
M('prism-side-scale','Сечение призмы через среднюю линию основания: боковые грани линейно масштабируются','exam-solid','Правильные призмы','exam-solid:5','exam-solid.21,exam-solid.22','partial','G5: нужно явно разобрать, что здесь высота та же: боковая площадь меняется в k, а не k²')
M('cone-volume-scale','Параллельное сечение конуса: линейный коэффициент и куб объёма','solid-geometry,exam-solid','Многогранники|Сечения','exam-solid:5','solid-geometry.20,solid-geometry.21')
M('pyramid-volume','Объём пирамиды/тетраэдра как треть площади основания на высоту','solid-geometry,exam-solid','Многогранники','exam-solid:5','solid-geometry.3,solid-geometry.16,exam-solid.17')
M('sphere-cone','Осевое сечение сферы/конуса, Пифагор и радиус описанной сферы','exam-solid','Сфера в теле и сфера около тела','exam-solid:2','exam-solid.32,exam-solid.33')
M('sphere-cylinder','Вписанный шар и описанный цилиндр: h=2r, площади и объёмы','exam-solid,solid-geometry','Сфера в теле и сфера около тела','solid-geometry:2','exam-solid.31,exam-solid.38,solid-geometry.6')
M('pyramid-area','Площадь правильной пирамиды через апофему и основание','exam-solid','Правильные призмы, пирамиды','exam-solid:2','exam-solid.23,exam-solid.24')
M('trig-value','Тождества, знаки четверти, формулы двойного угла/приведения','c15','Основные тождества|Котангенс и формулы сложения','','c15.4,c15.7,c15.8,c15.35')
M('log-value','Свойства логарифмов и переход к другому основанию','c14-exponential','Свойства логарифмов','','c14.7,c14.11,c14.19,c14.23')
M('power-value','Правила степеней, рациональные/иррациональные показатели','c06,c07,c14-exponential','Степени','','c06.3,c14.3')
M('formula-rational','Выразить переменную из заданной дробно-линейной физической формулы','exam-rational,exam-measurements','Равносильные|Прикидка','exam-rational:1','exam-rational.3,exam-measurements.20')
M('formula-quadratic','Подстановка в физическую формулу, квадратное уравнение, единицы и допустимое время','c11,exam-measurements','Величины и единицы','exam-measurements:5','c11.4,exam-measurements.4')
M('formula-radical','Выразить параметр из формулы с корнем, выбрать допустимый знак','exam-rational,exam-measurements','Иррациональные|Прикидка','exam-rational:4','exam-rational.6,exam-rational.8')
M('formula-log','Логарифмическая физическая модель: выразить величину через показатель','exam-exponential,exam-measurements','Логарифмические','exam-exponential:4','exam-exponential.10,c14.14')
M('formula-fourth','Физическая модель с четвёртой степенью и научной записью','c06,c07,exam-measurements','Прикидка','exam-measurements:5','exam-rational.36,c06.3')
M('river','Движение по/против течения, относительная скорость и уравнение времён','exam-models','Движение и средняя скорость','exam-models:2','exam-models.6,exam-models.3')
M('mixture','Система материального баланса двух опытов смешивания','exam-models,c11','Смеси, растворы и сохранение количества','exam-models:4','exam-models.11,exam-models.12,exam-models.15','partial','G3: все практические задачи на смеси проще; нужен разбор двух опытов с двумя неизвестными массами')
M('motion','Разность скоростей, уравнение времени на одном пути','exam-models','Движение и средняя скорость','exam-models:2','exam-models.2,exam-models.3,exam-models.4')
M('work','Постоянная производительность, сумма скоростей выполнения работы','exam-models','Работа и производительность','exam-models:3','exam-models.7,exam-models.8,exam-models.9')
M('ext-log','Экстремум функции с логарифмом: ОДЗ, производная, знаки/концы','c20','Исследование функции с помощью производной','c20:4','exam-calculus.2,exam-calculus.5')
M('ext-exp','Экстремум произведения многочлена и экспоненты','c20','Исследование функции с помощью производной','c20:3','exam-calculus.3,c20.4')
M('ext-rational','Экстремум рациональной функции','c20','Исследование функции с помощью производной','c20:3','exam-calculus.4,c20.31')
M('ext-trig','Экстремум функции с тригонометрическими множителями','c20,c15','Алгебра производных|Исследование функции','c20:3','c20.28,exam-calculus.1','partial','G6: нет полной практической задачи на знак производной произведения с тригонометрией на интервале')
M('ext-polynomial','Экстремум многочлена: производная и смена знака','c20','Исследование функции с помощью производной','c20:3','exam-calculus.1,exam-calculus.2')
M('trig-full','Преобразование уравнения, факторизация, несколько серий и точный отбор на отрезке','exam-trigonometric,c15','Отбор корней|Сведение к алгебре','exam-trigonometric:2,exam-trigonometric:3','exam-trigonometric.13,exam-trigonometric.21,exam-trigonometric.30')
M('log-ineq','ОДЗ сложного логарифмического неравенства; преобразование к рациональному и интервалам','exam-exponential,exam-rational','Логарифмические|Метод интервалов','exam-exponential:4,exam-exponential:5','exam-exponential.16,exam-exponential.28,exam-exponential.29','partial','G7: не хватает цельного многошагового разбора с полиномиальными аргументами и логарифмами в знаменателе')
M('exp-ineq','Дробное показательное неравенство через t=a^x>0 и метод интервалов','exam-exponential,exam-rational','Показательные|Метод интервалов','exam-exponential:3','exam-exponential.6,exam-exponential.9,exam-rational.20')
M('finance-schedule','График остатков долга, частичные проценты, суммы платежей по разным блокам','exam-models,c12-progressions','Кредит: остаток долга и платежи','exam-models:5,exam-models:6','exam-models.20,exam-models.21,exam-models.22,exam-models.24','partial','G3: нет сложного неоднородного графика долга и примера суммы за часть срока')
M('finance-annuity','Равные полные платежи, геометрическая прогрессия остатков','exam-models,c12-progressions','Кредит: остаток долга и платежи','exam-models:5','exam-models.23,exam-models.30')
M('optimization-profit','Квадратичная прибыль при переменной цене; оптимум, затем окупаемость','exam-models,c20,c17','Выбор лучшего варианта|Два средних','exam-models:7','exam-models.26,exam-models.27,c20.17','partial','G3: нет двухэтапного разбора «сначала максимальная прибыль по объёму, затем условие на цену»')
M('optimization-weighted','Распределение затрат между двумя производствами; взвешенное Коши–Буняковского','c17,exam-models','Неравенство Коши','exam-models:7','c17.26,exam-models.26','partial','G3: теорема есть; не показано приведение бюджетной модели к взвешенной сумме квадратов')
M('optimization-physics','Оптимизация физического выражения: область, замена, производная, глобальный максимум','c20,exam-models','Исследование функции с помощью производной','c20:3','exam-calculus.3,exam-calculus.4,c20.24','partial','G6: отсутствует прикладной разбор рациональной функции мощности/амплитуды с физическими ограничениями')
M('recover-graph','Восстановление коэффициентов функции по узловым точкам графика','c13,exam-functions,c11','Графики и преобразования','exam-functions:3','c13.6,c13.7,c13.12','partial','G4: есть построение по формуле; почти нет обратных задач «рисунок -> коэффициенты -> значение»')
M('intersection-graph','Восстановить по рисунку две формулы и найти второе пересечение','c13,exam-functions,c11','Графики и преобразования','exam-functions:3','c13.12,exam-functions.25','partial','G4: решение пересечения по известным формулам есть; восстановление обеих формул и скрытой точки не отработано')
M('solid-dihedral','Поставить координаты призмы, доказать ортогональность, найти угол плоскостей по нормалям','solid-geometry,exam-solid,c18','Углы и векторное произведение|Проекции','exam-solid:2','exam-solid.34,solid-geometry.13,c18.4')
M('solid-parallel-distance','Параллельные сечения пирамиды, расстояние точки до плоскости','exam-solid,solid-geometry','Взаимное расположение|Расстояние','exam-solid:5','exam-solid.1,exam-solid.9,solid-geometry.9')
M('solid-section','Координаты, точное построение сечения, длины/площадь/расстояние','exam-solid,solid-geometry','Сечения:|Координатный','exam-solid:4,exam-solid:5','exam-solid.16,exam-solid.17,exam-solid.20,exam-solid.35,exam-solid.37')
M('solid-prism-side','Отношения в ромбе/равнобедренном сечении призмы, неизвестная высота','exam-solid,solid-geometry','Сечения:|Координатный','exam-solid:4','exam-solid.16,exam-solid.21,exam-solid.34','partial','G5: есть метод сечения, но недостаточно многошаговых задач с неизвестной высотой и условием на вид сечения')
M('plane-advanced','Несколько геометрических фактов подряд: касательные, цикличность, подобие, площади/координаты','exam-plane,plane-geometry,c18','Окружности|Преобразования и дополнительные построения','exam-plane:5','exam-plane.34,exam-plane.36,exam-plane.37,exam-plane.38,plane-geometry.13','partial','G5: базовая теория подходит, но мало полных развёрнутых решений уровня последних геометрических задач')
M('param-circles','Единственное пересечение двух окружностей: расстояние центров и два вида касания','exam-parameters,plane-geometry','Системы с параметром|Графические пересечения','exam-parameters:5','exam-parameters.21,plane-geometry.19','partial','G1: разобрана прямая–окружность; нет критерия для двух окружностей d=R+r или d=|R−r| с исключением совпадения')
M('param-branches','Нелинейный параметр: выделить ветви, проверить ОДЗ, число различных точек и совпадения','exam-parameters,exam-rational','Модуль, корень и число решений|Системы с параметром','exam-parameters:6,exam-parameters:7','exam-parameters.17,exam-parameters.18,exam-parameters.25','partial','G1: нет полного разбора системы/уравнения из нескольких ветвей со слиянием решений')
M('param-interval','Иррациональное/модульное уравнение с параметром и ровно одним корнем на отрезке','exam-parameters,exam-rational','Корни на отрезке|Модуль, корень','exam-parameters:4','exam-parameters.11,exam-parameters.12,exam-parameters.25','partial','G1: отдельно отработаны отрезок и корень; не отработана их комбинация со сменой ветвей')
M('param-nonlinear','Нелинейная система с параметром на окружности: симметрия по x, кандидаты x=0, сумма неотрицательных слагаемых','exam-parameters,c13,c14-exponential,c17','Системы с параметром|Графики и преобразования|Свойства показательной и логарифмической функций|Знаки, квадраты и цепочки оценок','','exam-parameters.18,exam-parameters.21,c13.9,c17.7','partial','G1: нужен полный разбор симметричной системы с экспонентой, модулем и окружностью; элементарный приём не был раскрыт отдельным примером')
M('discrete-average','Натуральные числа, изменение среднего, ограничения делимости, нижняя оценка и конструкция','c21,c17,statistics','Уравнения в целых|Инварианты','statistics:1','c21.19,c21.21,c17.17,c17.28','partial','G2: нет полного разбора дискретного среднего и достижения границы при всех исходных ограничениях')
M('discrete-pair','Повторное преобразование пары; двойной ход, обратный ход, делимость и достижимость','c21,c17','Инварианты|Сравнения','', 'c17.18,c17.19,c17.27,c21.23','partial','G2: примеры инвариантов вводные; нет двойного преобразования, обратного восстановления и минимума')
M('discrete-subsets','Целочисленность средних произвольных подмножеств: сравнение двух наборов, общие остатки','c21,c17','Сравнения по модулю|Контрпример','', 'c21.22,c21.23,c21.26,c17.23','partial','G2: отсутствует приём «два поднабора отличаются одним элементом» и дальнейший подбор остатков')
M('discrete-cards','Различные числа в диапазонах: ёмкость множества, арифметическая оценка и пример достижения','c21,c17,c12-progressions','Уравнения в целых|Что значит оценить','', 'c17.17,c17.21,c21.21,c21.27','partial','G2: нет полного решения экстремума с разными цветами и числом доступных различных кратных')
M('discrete-coins','Ограниченные монеты, сравнения, интервалы достижимых сумм и минимальная добавка','c21,c17','Уравнения в целых','', 'c21.21,c21.27','partial','G2: есть линейное диофантово уравнение; нет покрытия всех сумм диапазона и минимального ресурса')
M('discrete-digits','Сумма цифр, делимость, ведущий ноль, конструкция и экстремальный перебор','c02,c21,c17','Признаки делимости|Сравнения','', 'c21.22,c21.27,c17.21','partial','G2: теория делимости есть; нет сочетания цифровых ограничений и доказательства максимума/минимума')
M('discrete-letters','Целочисленный баланс двух типов, ограничения размеров группы и сумма разных количеств','c21,c17,c12-progressions','Уравнения в целых|Что значит оценить','', 'c21.19,c21.21,c17.17','partial','G2: нет задачи на целочисленный баланс и нижнюю сумму попарно различных полученных количеств')
M('param-polynomial','Параметрическое многочленное уравнение: группировка, вырождение и совпадение корней','exam-parameters,c11','Параметр и особые значения|Модуль, корень и число решений','exam-parameters:1,exam-parameters:7','exam-parameters.3,exam-parameters.24','partial','G1: нет законченного разбора параметрического произведения с постоянной ветвью, линейным вырождением и совпадениями')
M('exp-polynomial-ineq','Смешанное неравенство: показательную часть факторизовать, многочлен от x сохранить, совместить нули и полюса','exam-exponential,exam-rational','Замены в показательных задачах|Метод интервалов','exam-exponential:3','exam-exponential.9,exam-rational.19','partial','G7: нет законченного разбора дроби с показательной частью в числителе и многочленом от x в знаменателе')
# A list entry corresponds to one numbered exam position. Lists enumerate every displayed ИЛИ alternative.
def P(k,brief=''):return (k,brief)
classic=[P('prob-classic','равномерный билет'),P('prob-nested','срок службы в интервале'),P('prob-repeat','хотя бы одно попадание')]
equations=[P('eq-exp','общий показатель'),P('eq-rad','один квадратный корень'),P('eq-log','логарифм линейного выражения'),P('eq-quad','выбрать меньший корень')]
angles=[P('circle-angle','центральный и вписанный углы'),P('midline','площадь малого треугольника'),P('rhombus-angle','диагональ ромба'),P('parallelogram','две высоты параллелограмма')]
solids=[P('cylinder-ratio','переливание в широкий цилиндр'),P('prism-side-scale','боковая поверхность части призмы'),P('cone-volume-scale','усечённая часть конуса')]
values=[P('trig-value','синус двойного угла по косинусу'),P('log-value','тождество логарифмов'),P('power-value','произведение степеней')]
derivs=[P('derivative-sign','знак f\' по f'),P('tangent-slope','наклон нарисованной касательной')]
words=[P('river','отношения скоростей по/против течения'),P('mixture','два опыта смешивания'),P('motion','разность скоростей после обгона')]
mins=[P('ext-log','абсолютный минимум на отрезке'),P('ext-exp','многочлен на экспоненту'),P('ext-rational','рациональный минимум')]
hard19=[P('trig-full','несколько серий и отбор'),P('solid-dihedral','призма: перпендикуляр и угол плоскостей'),P('log-ineq','разность логарифмов полиномов'),P('plane-advanced','две касающиеся окружности'),P('finance-schedule','таблица неодинаковых остатков долга'),P('param-circles','единственное пересечение окружностей'),P('discrete-average','переход ученика и целые средние')]
variants={}
variants[(2019,'demo')]=[P('time'),P('data-read'),P('grid-area'),classic[0],equations[0],angles[0],derivs[0],solids[0],values[0],P('formula-rational','частота отражённого сигнала'),words[0],P('ext-log','локальный максимум с логарифмом')]+hard19
base20=[[P('time'),P('ceil'),P('percent'),P('floor-index')],[P('data-read','осадки'),P('data-read','электрическое сопротивление'),P('data-read','столбцы температур')],[P('grid-area'),P('midline','трапеция на клетчатой бумаге')],classic,equations,angles,derivs,solids,values,P('formula-rational','частота сигнала'),words,mins]
variants[(2020,'demo')]=base20+hard19
v21=copy.deepcopy(base20);v21[10].append(P('work','две трубы с разницей времён'));v21[11].append(P('ext-trig','произведение с синусом и косинусом'))
h21=list(hard19);h21[1]=[hard19[1],P('solid-parallel-distance','пирамида: параллельные плоскости и расстояние')];h21[4]=[hard19[4],P('optimization-profit','цена для трёхлетней окупаемости')];h21[6]=[hard19[6],P('discrete-average','шесть малых и шесть больших из десяти чисел')]
variants[(2021,'demo')]=v21+h21
cond=[P('prob-cond','три кубика при заданной сумме'),P('prob-total','доля пенсионеров среди мужчин')]
h22=[hard19[0],hard19[1],hard19[2],hard19[4],hard19[3],hard19[5],hard19[6]]
variants[(2022,'demo')]=[equations,classic[:2],angles,values,solids,derivs,P('formula-rational'),words,P('recover-graph','квадратичная функция по рисунку'),cond,mins]+h22
variants[(2023,'demo')]=[angles,solids,classic[:2],cond,equations,values,derivs,P('formula-rational'),words,P('recover-graph','квадратичная функция по рисунку'),mins]+h22
vec=[P('vector-dot','координаты снять с рисунка'),P('vector-length','длина линейной комбинации')]
h24=[hard19[0],P('solid-section','трёхгранный прямой тетраэдр и площадь сечения'),hard19[2],P('finance-schedule','долг убывает двумя разными арифметическими блоками'),hard19[3],hard19[5],P('discrete-pair','итерация суммы и разности')]
variants[(2024,'demo')]=[angles,vec,solids,classic[:2],cond,equations,values,derivs,P('formula-rational'),words,P('recover-graph'),mins]+h24
ang25=[P('circle-angle','вписанный четырёхугольник'),P('parallelogram','вычесть треугольник из параллелограмма'),P('triangle-angle','внешний угол равнобедренного треугольника'),P('midline','деление средней линии диагональю')]
sol25=[P('cylinder-ratio','отношение объёмов кружек'),P('pyramid-area','правильная квадратная пирамида'),P('cone-volume-scale','долить конический сосуд')]
prob25=[P('prob-classic','попадание человека в случайную команду'),P('prob-nested','число пассажиров в целочисленном интервале')]
p25=[P('prob-repeat','хотя бы одна целая лампа'),P('prob-draw','два разных заданных цвета')]
words25=[P('river','два пути и разность времён'),words[1],P('work','разность расходов двух труб')]
h25=[P('trig-full','кубическое выражение с тригонометрией'),P('solid-section','сечение правильного тетраэдра перпендикулярно линии середин'),P('log-ineq','дробь с логарифмами в знаменателе'),h24[3],P('plane-advanced','вписанный пятиугольник'),P('param-branches','иррациональная система с прямой'),h24[6]]
variants[(2025,'demo')]=[ang25,vec,sol25,prob25,p25,equations,values,[P('derivative-sign','рост по f\''),derivs[1]],P('formula-rational','минимальная различимая доплеровская частота'),words25,P('intersection-graph','парабола и прямая'),mins]+h25
ang26=[ang25[0],ang25[1],P('right-median','угол между высотой и медианой'),ang25[3]]
sol26=[sol25[0],P('pyramid-volume','пятивершинная часть параллелепипеда'),sol25[2],P('sphere-cone','сфера около конуса')]
prob26=prob25+[P('prob-classic','позиция в случайном порядке докладов')]
p26=p25+[P('prob-union','масса между двумя порогами'),P('prob-union','кофе в обоих зависимых автоматах')]
v26=[P('vector-dot','векторы по рисунку'),P('vector-length','длина линейной комбинации'),P('vector-dot','координаты заданы')]
d26=[P('derivative-extremum','число максимумов на отрезке'),P('derivative-sign','точки возрастания'),P('tangent-slope','коэффициент нарисованной касательной')]
f26=[P('formula-quadratic','разгон и перевод часов в минуты'),P('formula-rational','порог доплеровской частоты'),P('formula-radical','ускорение через путь и скорость')]
g26=[P('recover-graph','гипербола'),P('intersection-graph','парабола и прямая'),P('recover-graph','показательная функция')]
h26=[[h25[0],P('trig-full','корни с дополнительными радикальными выражениями')],[h25[1],P('solid-section','равностороннее сечение квадратной пирамиды')],[h25[2],P('exp-polynomial-ineq','куб от3^x−3 и квадратный знаменатель от x')],[h25[3],P('finance-schedule','сумма платежей только второго года')],[h25[4],P('plane-advanced','две высоты параллелограмма')],[h25[5],P('param-branches','модули с квадратными выражениями')],[h25[6],P('discrete-subsets','целые средние любых четырёх и пяти')]]
variants[(2026,'demo')]=[ang26,v26,sol26,prob26,p26,equations,values,d26,f26,[P('motion','догоняющий теплоход'),words[1],words25[2]],g26,mins+[P('ext-polynomial','кубическая функция')]]+h26
h27=[[P('trig-full','квадратный тригонометрический многочлен'),P('trig-full','косинусы сдвинутых аргументов')],[P('solid-section','шестиугольная пирамида: объём по двугранному углу'),P('solid-section','тетраэдр: отношение объёмов и угол')],[P('log-ineq','логарифмы и вложенные аргументы'),P('exp-ineq','дробная функция от 8^x')],[P('optimization-physics','максимальная мощность на нагрузке'),P('optimization-physics','максимальная амплитуда качки')],[P('plane-advanced','вписанная окружность и высота'),P('plane-advanced','касательные и диаметр')],[P('param-branches','модульная парабола и прямая'),P('param-polynomial','полиномиальное уравнение после факторизации на три множителя')],[P('discrete-cards','синие и красные кратные в ограниченном диапазоне'),P('discrete-coins','монеты двух номиналов и добавка единичных')]]
variants[(2027,'demo')]=[[P('tangential-quad'),P('midline','площадь трапеции под средней линией'),P('triangle-angle','биссектриса и угол при точке на стороне')],v26,[P('prism-side-scale'),P('pyramid-volume','тетраэдр внутри параллелепипеда'),P('sphere-cylinder')],prob26,[P('prob-repeat','заданная последовательность попаданий'),P('prob-total','контроль качества батареек'),P('prob-union','масса между порогами')],P('expectation','таблица выигрышей'),equations[:3],values,[P('derivative-extremum','число минимумов на отрезке'),derivs[0],derivs[1]],[P('formula-quadratic','торможение до остановки'),P('formula-log','разряд конденсатора'),P('formula-radical','разгон по пути')],[P('motion','велосипедисты с разным временем'),words[1],P('work','изготовление деталей с разностью производительностей')],g26,P('finance-annuity','три равных полных платежа')]+h27
variants[(2024,'open')]=[P('triangle-angle'),P('vector-dot'),P('sphere-cylinder'),P('prob-nested'),P('prob-cond','два кубика при отсутствии шестёрок'),P('eq-exp'),P('log-value'),P('derivative-extremum'),P('formula-radical'),P('motion'),P('recover-graph'),P('ext-polynomial'),P('trig-full'),P('solid-prism-side','ромбическое сечение призмы'),P('log-ineq'),P('optimization-weighted'),P('plane-advanced','основания высот и центр описанной окружности'),P('param-interval','иррациональное уравнение на [0;1]'),P('discrete-digits','две кратные45 из заданных цифр')]
variants[(2025,'open')]=[P('parallelogram'),P('vector-dot','скалярное произведение двух комбинаций'),P('cylinder-ratio','цилиндр внутри параллелепипеда'),P('prob-repeat','ровно указанная игра с мячом'),P('prob-repeat'),P('eq-log'),P('trig-value'),P('derivative-sign'),P('formula-quadratic'),P('work'),P('intersection-graph','корень и прямая'),P('ext-exp'),P('trig-full'),P('solid-prism-side','равнобедренный треугольник сечения'),P('log-ineq'),P('optimization-profit'),P('plane-advanced','диагонали трапеции и перенос'),P('param-branches','модуль, квадрат и корень'),P('discrete-letters','разные количества писем и баланс')]
variants[(2026,'open')]=[P('triangle-angle'),P('vector-length'),P('pyramid-volume','конус и цилиндр с общей высотой'),P('prob-union','несовместные вопросы'),P('prob-draw'),P('eq-rad'),P('trig-value'),P('derivative-extremum'),P('formula-fourth'),P('mixture','сплавы с заданной разностью масс'),P('recover-graph'),P('ext-log'),P('trig-full'),P('solid-section','трапеция сечения призмы и расстояние'),P('log-ineq'),P('finance-schedule','проценты без уменьшения долга и два равных последних платежа'),P('plane-advanced','две медианные конструкции и след прямой'),P('param-nonlinear','показательная функция с модулем на окружности'),P('discrete-digits','разные числа с равной суммой цифр')]
# Exact section vocabulary in the reviewed source; do not infer from chapter names.
section_overrides={
 'prob-classic':'Исходы, события и вероятность', 'prob-nested':'Исходы, события и вероятность',
 'prob-total':'Условная вероятность и формула Байеса', 'prob-union':'Исходы, события и вероятность',
 'expectation':'Среднее, дисперсия и совместные величины|Разборы распределений',
 'eq-exp':'Основание и направление сравнения|Замены в показательных задачах',
 'eq-log':'ОДЗ и преобразования логарифмов|Свойства показательной и логарифмической функций',
 'vector-dot':'Координаты точки и координаты перемещения|Примеры: векторы',
 'vector-length':'Координаты точки и координаты перемещения|Линейная комбинация',
 'log-value':'Правила степеней и логарифмов с условиями',
 'power-value':'Свойства степеней|Правила степеней и логарифмов с условиями',
 'formula-log':'ОДЗ и преобразования логарифмов|Прикидка и проверка размерности',
 'trig-full':'Периодичность и отбор на промежутке|Квадратные и однородные уравнения|Сумма в произведение',
}
for k,v in section_overrides.items():methods[k]['section_searches']=v.split('|')
methods['circle-angle']['task_uids']=['plane-geometry.11','exam-plane.24']
methods['time']['task_uids']=['exam-measurements.4']
# Resolve the evidence to actual source sections and literal exercise text.
for key,m in methods.items():
 m['chapters']=[{'id':cid,'number':chapters[cid][0],'title':chapters[cid][1]['title']} for cid in m['chapter_ids']]
 m['theory_sections']=[]
 for cid in m['chapter_ids']:
  s=re.findall(r'\\section\{([^}]+)\}',chapters[cid][1]['theory'])
  for title in s:
   if any(x.lower() in title.lower() for x in m['section_searches']):m['theory_sections'].append({'chapter_id':cid,'title':title})
 assert m['theory_sections'],('No exact section match',key)
 for e in m['example_refs']:
  source=re.findall(r'\\begin\{example\}(.*?)\\end\{example\}',chapters[e['chapter_id']][1]['theory'],re.S)
  assert len(source)>=e['ordinal'],(key,e)
  e['audit_ref']=f"{e['chapter_id']}.example.{e['ordinal']}";e['text']=source[e['ordinal']-1].strip()
 m['tasks']=[]
 for uid in m['task_uids']:
  assert uid in alltasks,(key,uid)
  ch,cid,n,t=alltasks[uid];m['tasks'].append({'uid':uid,'chapter_id':cid,'published_number':f'{ch}.{n}','question':t['q']})
rows=[]
for (year,kind),positions in sorted(variants.items()):
 for no,v in enumerate(positions,1):
  alts=v if isinstance(v,list) else [v]
  for alt,(key,brief) in enumerate(alts,1):
   assert key in methods
   m=methods[key]
   rows.append({'year':year,'variant_kind':kind,'task_number':no,'alternative':alt,'brief':brief or m['description'],'method_id':key,'required_method':m['description'],'status':m['status'],'gap':m['gap'],'chapter_ids':m['chapter_ids'],'theory_sections':m['theory_sections'],'example_refs':[x['audit_ref'] for x in m['example_refs']],'task_uids':m['task_uids']})
# Verified PDFs and sources (archive provenance is preserved in manifests).
sel=json.loads((OUT/'selected-variants.json').read_text())
openmeta=json.loads((OUT/'manifest-open-downloads.json').read_text())
for r in openmeta:
 for f in r.get('files',[]):
  if 'проф' in f['archive_member'].lower():sel.append({'year':r['year'],'kind':'open',**f,'selected_pdf':f['path'],'url':r['url']})
demosmeta={r['year']:r for r in json.loads((OUT/'manifest-downloads.json').read_text())}
for v in sel:
 v['pdf_sha256']=hashlib.sha256((ROOT/v['selected_pdf']).read_bytes()).hexdigest()
 if v['kind']=='demo':v['url']=demosmeta[v['year']]['url'] if v['year']<2027 else 'https://doc.fipi.ru/ege/demoversii-specifikacii-kodifikatory/2027/ma_11_2027.zip'
 v['numbered_positions']=len(variants[(v['year'],v['kind'])]);v['alternative_examples']=sum(r['year']==v['year'] and r['variant_kind']==v['kind'] for r in rows)
assert len(sel)==12
source_index={(v['year'],v['kind']):v for v in sel}
for r in rows:
 v=source_index[(r['year'],r['variant_kind'])]
 r.update(source_url=v['url'],source_pdf=v['selected_pdf'],source_sha256=v['pdf_sha256'])
result={'checked_at':'2026-10-24','book_data_sha256':hashlib.sha256(bookpath.read_bytes()).hexdigest(),'snapshot_chapters':len(book),'snapshot_tasks':len(alltasks),'scope':'9 official demos 2019–2027, every displayed alternative, plus official open variants2024–2026; no guarantee of arbitrary possible task','official_pages':['https://fipi.ru/ege/demoversii-specifikacii-kodifikatory','https://fipi.ru/ege/otkrytyy-bank-zadaniy-ege/otkrytyye-varianty-kim-ege'],'sources':sorted(sel,key=lambda x:(x['year'],x['kind'])),'position_count':sum(len(v) for v in variants.values()),'alternative_example_count':len(rows),'methods':methods,'rows':rows,'status_counts':dict(collections.Counter(r['status'] for r in rows))}
(OUT/'coverage.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
fields=['source_url','source_pdf','source_sha256','year','variant_kind','task_number','alternative','brief','method_id','required_method','status','gap','chapter_ids','theory_sections','example_refs','task_uids']
with (OUT/'coverage.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader()
 for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
print(json.dumps({k:result[k] for k in ['position_count','alternative_example_count','status_counts','snapshot_chapters','snapshot_tasks']},ensure_ascii=False,indent=2))
print([(v['year'],v['kind'],v['numbered_positions'],v['alternative_examples']) for v in result['sources']])
