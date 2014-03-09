__author__ = 'gleb'

from pole_extractor import diagram_calculator
import graphine

labels = ('e111|e|', 'ee11|22|ee|', 'ee12|e22|e|', 'e112|22|e|', 'ee11|22|33|ee|', 'ee11|23|e33|e|', 'ee12|ee3|333||',
          'ee12|e33|e33||', 'e112|e3|e33|e|', 'ee12|e23|33|e|', 'e123|e23|e3|e|', 'ee12|223|3|ee|')

for l in labels:
    g = graphine.Graph.fromStr(l)
    diagram_calculator.calculate_diagram(label=l, theory=4, max_eps=4,
                                         zero_momenta=True, force_update=False)
    if 2 == g.externalEdgesCount():
        diagram_calculator.calculate_diagram(label=l, theory=4, max_eps=4,
                                             zero_momenta=False, force_update=False)

    diagram_calculator.calculate_rprime(l, PHI_EXPONENT=4, force_update=True, verbose=2)