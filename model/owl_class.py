from os import path
from model.entity import *
from jinja2 import Environment, FileSystemLoader
import markdown


class OwlClasses(Entities):
    def __init__(self, g, existing_fids):
        super().__init__(g, existing_fids)

        self.instances = []

        q = '''
            PREFIX owl:  <http://www.w3.org/2002/07/owl#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>     
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX dct:  <http://purl.org/dc/terms/>
            SELECT * 
            WHERE {
                ?uri    a   owl:Class .                  
            }
        '''

        for r in g.query(q):
            self.instances.append(
                OwlClass(self.g, str(r.uri), self.existing_fids)
            )

    @property
    def html(self):
        template_dir = path.join(path.dirname(path.dirname(path.realpath(__file__))), 'templates')
        template = Environment(loader=FileSystemLoader(template_dir)).get_template('classes.html')
        return template.render(
            instances=self.instances
        )


class OwlClass(Entity):
    def __init__(self, g, uri, existing_fids):
        super().__init__(g, uri, existing_fids)

    @property
    def html(self):
        template_dir = path.join(path.dirname(path.dirname(path.realpath(__file__))), 'templates')
        template = Environment(loader=FileSystemLoader(template_dir)).get_template('class.html')
        return template.render(
            uri=self.uri,
            fid=self.fid,
            name=self.name,
            description=self.description,
            usage=self.usage
        )


if __name__ == '__main__':
    from rdflib import Graph
    import owlrl

    # used to capture graph parsing and content errors
    class RdfGraphError(Exception):
        pass

    existing_fids = []

    g = Graph().parse(path.join(path.dirname(path.dirname(path.realpath(__file__))), 'examples', 'prof.ttl'), format='turtle')

    # expand the graph using OWL-RL
    try:
        owlrl.DeductiveClosure(owlrl.RDFS_OWLRL_Semantics).expand(g)
    except Exception as e:
        raise RdfGraphError(
            'Error while running OWL-RL Deductive Closure\n{}'.format(str(e.args[0]))
        )

    ocs = OwlClasses(g, existing_fids)

    print(ocs.html)
