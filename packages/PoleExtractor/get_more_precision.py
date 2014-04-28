__author__ = 'Gleb Dovzhenko <dovjenko.g@gmail.com>'

from pole_extractor import diagram_calculator

diagrams_p0 = ('e12|23|4|e5|56|7|78|8|e|', 'e12|23|4|e5|67|68|7|8|e|', 'e12|23|4|e5|67|68|8|e8||',
               'e12|23|4|e5|67|88|e7|8||', 'e12|e3|45|46|5|7|78|8|e|', 'e12|e3|45|67|e5|8|78|8||',
               'e12|e3|34|5|67|68|7|8|e|', 'e12|e3|44|56|5|7|78|8|e|')

diagrams_p2 = ('e12|23|4|e5|56|7|77||', 'e12|23|4|e5|67|67|7||', 'e12|23|4|56|57|6|7|e|', 'e12|23|4|45|6|e7|77||',
               'e12|e3|45|46|5|7|77||', 'e12|33|45|6|56|7|7|e|', 'e12|33|45|6|e7|67|7||', 'e12|23|4|e5|66|77|7||')


for d in diagrams_p2:
    diagram_calculator.calculate_diagram(label=d, theory=3, max_eps=-1, zero_momenta=False,
                                         force_update=False, adaptive=False)
    diagram_calculator.calculate_rprime(label=d, theory=3)