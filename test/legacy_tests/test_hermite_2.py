from legacy_support import TestWithMPI
import sys

from amuse.legacy.hermite0.interface import Hermite

from amuse.support.data import core
from amuse.support.units import nbody_system
from amuse.support.units import units

import numpy

try:
    from matplotlib import pyplot
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class TestMPIInterface(TestWithMPI):

    def test0(self):
        instance = Hermite()
        self.assertTrue("Hut" in instance.all_literature_references_string())
    
    def test1(self):
        instance = Hermite()
        instance.setup_module()

        res1 = instance.new_particle(mass = 11.0, radius = 2.0, x = 0.0, y = 0.0, z = 0.0, vx = 0.0, vy = 0.0, vz = 0.0)
        res2 = instance.new_particle(mass = 21.0, radius = 5.0, x = 10.0, y = 0.0, z = 0.0, vx = 10.0, vy = 0.0, vz = 0.0)
        
        self.assertEquals(0, res1['index_of_the_particle'])
        self.assertEquals(1, res2['index_of_the_particle'])

        retrieved_state1 = instance.get_state(0)
        retrieved_state2 = instance.get_state(1)

        self.assertEquals(11.0,  retrieved_state1['mass'])
        self.assertEquals(21.0,  retrieved_state2['mass'])
        self.assertEquals(0.0,  retrieved_state1['x'])
        self.assertEquals(10.0,  retrieved_state2['x'])

        instance.cleanup_module()
        del instance

    def test2(self):
        instance = Hermite()
        instance.setup_module()

        for i in [0, 1, 2]:
            temp_particle = instance.new_particle(mass = i, radius = 1.0, x = 0.0, y = 0.0, z = 0.0, vx = 0.0, vy = 0.0, vz = 0.0)
            self.assertEquals(i, temp_particle['index_of_the_particle'])
            
        instance.delete_particle(1)
      
        self.assertEquals(2, instance.get_number_of_particles()['number_of_particles'])
        
        self.assertEquals(0, instance.get_index_of_first_particle()['index_of_the_particle'])
        
        self.assertEquals(2, instance.get_index_of_next_particle(0)['index_of_the_next_particle'])
        self.assertEquals(0, instance.get_index_of_next_particle(0)['__result'])
        self.assertEquals(-1, instance.get_index_of_next_particle(1)['__result'])
        self.assertEquals(1, instance.get_index_of_next_particle(2)['__result'])
        
    def test3(self):
        hermite = Hermite()
        hermite.eps2 = 0.101
        self.assertEquals(0.101, hermite.eps2)
        hermite.eps2 = 0.110
        self.assertEquals(0.110, hermite.eps2)
        del hermite

    def test4(self):
        hermite = Hermite()
        hermite.flag_collision = 1
        self.assertEquals(1, hermite.flag_collision)
        hermite.flag_collision = 0
        self.assertEquals(0, hermite.flag_collision)
        del hermite

    def test5(self):
        hermite = Hermite()
        hermite.setup_module()
        
        hermite.new_particle([10,20],[1,1],[0,0],[0,0], [0,0], [0,0], [0,0], [0,0])
        retrieved_state = hermite.get_state(0)
        
        self.assertEquals(10.0,  retrieved_state['mass'])
        self.assertEquals(1, retrieved_state['radius'])

        retrieved_state = hermite.get_state([0,1])
        self.assertEquals(20.0,  retrieved_state['mass'][1])
        self.assertEquals(hermite.get_number_of_particles()['number_of_particles'], 2)
        hermite.cleanup_module()
        
#these tests involve higher level interface, which is not yet updated to comply with 
#new low level interface. Therefore currently dissabled

class TestAmuseInterface(TestWithMPI):
    def new_system_of_sun_and_earth(self):
        stars = core.Stars(2)
        sun = stars[0]
        sun.mass = units.MSun(1.0)
        sun.position = units.m(numpy.array((0.0,0.0,0.0)))
        sun.velocity = units.ms(numpy.array((0.0,0.0,0.0)))
        sun.radius = units.RSun(1.0)

        earth = stars[1]
        earth.mass = units.kg(5.9736e24)
        earth.radius = units.km(6371) 
        earth.position = units.km(numpy.array((149.5e6,0.0,0.0)))
        earth.velocity = units.ms(numpy.array((0.0,29800,0.0)))
        
        return stars
        
    def donttest2(self):
        convert_nbody = nbody_system.nbody_to_si(1.0 | units.MSun, 149.5e6 | units.km)

        instance = Hermite(convert_nbody)
        instance.parameters.epsilon_squared = 0.0 | units.AU**2
        instance.setup_module()
        instance.dt_dia = 5000
        
        stars = self.new_system_of_sun_and_earth()
        earth = stars[1]
        instance.new_particles(stars)
    
        for x in range(1,2000,10):
            instance.evolve_model(x | units.day)
            instance.update_particles(stars)
        
        if HAS_MATPLOTLIB:
            figure = pyplot.figure(figsize = (40,40))
            plot = figure.add_subplot(1,1,1)
            
            
            for index, (time,position) in enumerate(earth.position.values):
                x_point = position.value_in(units.AU)[0]
                y_point = position.value_in(units.AU)[1]
                color = 'b'
                plot.plot([x_point],[y_point], color + 'o')
            
            figure.savefig("hermite-earth-sun2.svg")    
        
        instance.cleanup_module()
        del instance

    def donttest1(self):
        convert_nbody = nbody_system.nbody_to_si(1.0 | units.MSun, 149.5e6 | units.km)

        hermite = Hermite(convert_nbody)
        hermite.parameters.epsilon_squared = 0.0 | units.AU**2
        hermite.setup_module()
        hermite.dt_dia = 5000
        
        stars = self.new_system_of_sun_and_earth()
        earth = stars[1]
                
        hermite.new_particles(stars)
        
        hermite.evolve_model(365.0 | units.day)
        hermite.update_particles(stars)
        
        position_at_start = earth.position.get_value_at_time(0 | units.s)[1].value_in(units.AU)[0]
        print position_at_start#0.999
        position_after_full_rotation = earth.position.value().value_in(units.AU)[0]
        print position_after_full_rotation
        #self.assertAlmostEqual(postion_at_start, postion_after_full_rotation, 6)
        
        hermite.evolve_model(365.0 + (365.0 / 2) | units.day)
        
        hermite.update_particles(stars)
        position_after_half_a_rotation = earth.position.value().value_in(units.AU)[0]
        print position_after_half_a_rotation
        self.assertAlmostEqual(-position_at_start, position_after_half_a_rotation, 2)
                
        hermite.evolve_model(365.0 + (365.0 / 2) + (365.0 / 4)  | units.day)
        
        hermite.update_particles(stars)
        position_after_half_a_rotation = earth.position.value().value_in(units.AU)[1]
        self.assertAlmostEqual(-position_at_start, postion_after_half_a_rotation, 3)
        
        hermite.cleanup_module()
        
        del hermite
        
