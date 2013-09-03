"""
Unit tests for SYMORO modules
"""
import unittest
import symoro
import geometry
#import kinematics
import invgeom
#import dynamics
from sympy import sympify,var, Matrix
from sympy.abc import A,B,C,X,Y,Z
from numpy import random, amax, matrix, eye, zeros

class testSymoroTrig(unittest.TestCase):

    def setUp(self):
        self.symo = symoro.Symoro()

    def test_GetMaxCoef(self):
        expr1 = A*B*X + C**2 - X
        expr2 = Y*Z - B
        self.assertEqual(symoro.get_max_coef(expr1*X + expr2, X), expr1)
        expr3 = -A**3*B**2*X**5*(X-Y)**7
        expr3x = -A**3*B**2*X**5*(-X-Y)**7
        expr3y = -A**3*B**2*X**5*(-X+Y)**7
        expr4 = B*X**2*(X-Y)**3
        self.assertEqual(symoro.get_max_coef(expr3*expr4, expr4), expr3)
        self.assertEqual(symoro.get_max_coef(expr3x, expr4), symoro.ZERO)
        res = symoro.get_max_coef(expr3y, expr4)*expr4-expr3y
        self.assertEqual(res.expand(), symoro.ZERO)

    def test_name_extraction(self):
        expr1 = sympify("C2*S3*R + S2*C3*R")
        self.assertEqual(symoro.get_trig_couple_names(expr1),{'2','3'})
        expr2 = sympify("CG2*S3*R + SG2*C1*R")
        self.assertEqual(symoro.get_trig_couple_names(expr2),{'G2'})
        expr2 = sympify("CA2*SA3*R + SG2*C3*R")
        self.assertEqual(symoro.get_trig_couple_names(expr2),set())
        expr3 = sympify("C2*S3*R + S1*C4*R")
        self.assertEqual(symoro.get_trig_couple_names(expr3),set())

    def test_name_operations(self):
        self.assertEqual(symoro.reduce_str('12','13'),('2','3'))
        self.assertEqual(symoro.reduce_str('124','123'),('4','3'))
        self.assertEqual(symoro.reduce_str('124','134'),('2','3'))
        self.assertEqual(symoro.reduce_str('12','124'),('','4'))
        self.assertEqual(symoro.reduce_str('1G2','G24'),('1','4'))
        self.assertEqual(symoro.reduce_str('1G2G4','13G4'),('G2','3'))

    def test_try_opt(self):
        e1 = A*(B-C)*X**2 + B*X**3 + A*(B-C)*Y**2 + B*X*Y**2
        e2 = X**2
        e3 = Y**2
        e4 = symoro.ONE
        e5 = symoro.ZERO
        self.assertEqual(self.symo.try_opt(e4,e5,e2,e3,e1),A*(B-C) + B*X)
        e6 = A*(B-C)*X**2 + B*X**3 - A*(B - C)*Y**2 - B*X*Y**2
        self.assertEqual(self.symo.try_opt(e4,e5,e2,e3,e6),e5)
        e7 = A*B
        self.assertEqual(self.symo.try_opt(e4,e7,e2,e3,e6),
                         e7*A*(B-C) + e7*B*X)
        self.assertEqual(self.symo.try_opt(e7,e4,e2,e3,e1),
                         e7*A*(B-C) + e7*B*X)

    def test_trig_simp(self):
        e1 = sympify("S2**2 + C2**2")
        e1ans = sympify("1")
        self.assertEqual(self.symo.C2S2_simp(e1),e1ans)
        e1 = sympify("S1**2 + C2**2")
        self.assertEqual(self.symo.C2S2_simp(e1),e1)
        e1 = sympify("S2**3 + C2**2")
        self.assertEqual(self.symo.C2S2_simp(e1),e1)
        e1 = sympify("S2**2 + 2*C2**2")
        e1ans = sympify("C2**2 + 1")
        self.assertEqual(self.symo.C2S2_simp(e1),e1ans)
        e1 = sympify("S1**2 + S1**2*C1 + C1**2 + C1**3 + C1**4")
        e1ans = sympify("C1**4 + C1 + 1")
        self.assertEqual(self.symo.C2S2_simp(e1),e1ans)
        e2 = sympify("C1*S2 - C2*S1")
        e2ans = sympify("-S1m2")
        self.assertEqual(self.symo.CS12_simp(e2),e2ans)
        e2 = sympify("C2*D3*S3m78 - C2m7*D8*S3 - C3*D8*S2m7 - C3m78*D3*S2 + D2*S3")
        e2ans = sympify("D2*S3 - D3*S278m3 - D8*S23m7")
        self.assertEqual(self.symo.CS12_simp(e2),e2ans)
        e3 = sympify("-a1*sin(th2+th1)*sin(th3)*cos(th1) - a1*cos(th1)*cos(th2+th1)*cos(th3)")
        e3ans = sympify("-a1*cos(th1)*cos(th1 + th2 - th3)")
        self.assertEqual(self.symo.CS12_simp(e3),e3ans)
        e4 = sympify("""C2*C3*C4**2*C5**2*C6**4*D3**2*RL4*S5 +
            2*C2*C3*C4**2*C5**2*C6**2*D3**2*RL4*S5*S6**2 +
            C2*C3*C4**2*C5**2*D3**2*RL4*S5*S6**4 +
            C2*C3*C4**2*C6**4*D3**2*RL4*S5**3 +
            2*C2*C3*C4**2*C6**2*D3**2*RL4*S5**3*S6**2 +
            C2*C3*C4**2*D3**2*RL4*S5**3*S6**4 +
            C2*C3*C5**2*C6**4*D3**2*RL4*S4**2*S5 +
            2*C2*C3*C5**2*C6**2*D3**2*RL4*S4**2*S5*S6**2 +
            C2*C3*C5**2*D3**2*RL4*S4**2*S5*S6**4 +
            C2*C3*C6**4*D3**2*RL4*S4**2*S5**3 +
            2*C2*C3*C6**2*D3**2*RL4*S4**2*S5**3*S6**2 +
            C2*C3*D3**2*RL4*S4**2*S5**3*S6**4 -
            C3*C4**2*C5**2*C6**4*D3*RL4**2*S23*S5 -
            2*C3*C4**2*C5**2*C6**2*D3*RL4**2*S23*S5*S6**2 -
            C3*C4**2*C5**2*D3*RL4**2*S23*S5*S6**4 -
            C3*C4**2*C6**4*D3*RL4**2*S23*S5**3 -
            2*C3*C4**2*C6**2*D3*RL4**2*S23*S5**3*S6**2 -
            C3*C4**2*D3*RL4**2*S23*S5**3*S6**4 -
            C3*C5**2*C6**4*D3*RL4**2*S23*S4**2*S5 -
            2*C3*C5**2*C6**2*D3*RL4**2*S23*S4**2*S5*S6**2 -
            C3*C5**2*D3*RL4**2*S23*S4**2*S5*S6**4 -
            C3*C6**4*D3*RL4**2*S23*S4**2*S5**3 -
            2*C3*C6**2*D3*RL4**2*S23*S4**2*S5**3*S6**2 -
            C3*D3*RL4**2*S23*S4**2*S5**3*S6**4""")
        e4ans = sympify("C3*D3*RL4*S5*(C2*D3 - RL4*S23)")
        self.assertEqual((self.symo.simp(e4)-e4ans).expand(), symoro.ZERO)


class testGeometry(unittest.TestCase):

    def setUp(self):
        self.symo = symoro.Symoro()
        self.robo = symoro.Robot.RX90()

    def test_dgm_RX90(self):
        T = geometry.dgm(self.robo, self.symo, 0, 6, fast_form=True, trig_subs=True)
        f06 = self.symo.gen_func('DGM_generated1', T, self.robo.get_q_vec())
        T = geometry.dgm(self.robo, self.symo, 6, 0, fast_form=True, trig_subs=True)
        f60 = self.symo.gen_func('DGM_generated2', T, self.robo.get_q_vec())
        for x in xrange(10):
            arg = random.normal(size = 6)
            self.assertLess(amax(matrix(f06(arg))*matrix(f60(arg))-eye(4)), 1e-12)
        t06 = matrix([[1,0,0,1],[0,1,0,0],[0,0,1,1],[0,0,0,1]])
        self.assertLess(amax(matrix(f06(zeros(6)))-t06), 1e-12)
        T46 = geometry.dgm(self.robo, self.symo, 4, 6, fast_form=False, trig_subs=True)
        C4,S4,C5,C6,S5,S6,RL4 = var("C4,S4,C5,C6,S5,S6,RL4")
        T_true46 = Matrix([[C5*C6,-C5*S6,-S5,0],[S6,C6,0,0],
                         [S5*C6,-S5*S6,C5,0],[0,0,0,1]])
        self.assertEqual(T46, T_true46)
        T36 = geometry.dgm(self.robo, self.symo, 3, 6, fast_form=False, trig_subs=True)
        T_true36 = Matrix([[C4*C5*C6-S4*S6,-C4*C5*S6-S4*C6,-C4*S5,0],
                         [S5*C6,-S5*S6,C5,RL4],
                         [-S4*C5*C6-C4*S6,S4*C5*S6-C4*C6,S4*S5,0],[0,0,0,1]])
        self.assertEqual(T36, T_true36)

    def test_dgm_SR400(self):
        self.robo = symoro.Robot.SR400()
        T = geometry.dgm(self.robo, self.symo, 0, 6, fast_form=True, trig_subs=True)
        f06 = self.symo.gen_func('DGM_generated1', T, self.robo.get_q_vec())
        T = geometry.dgm(self.robo, self.symo, 6, 0, fast_form=True, trig_subs=True)
        f60 = self.symo.gen_func('DGM_generated2', T, self.robo.get_q_vec())
        for x in xrange(10):
            arg = random.normal(size = 10)
            self.assertLess(amax(matrix(f06(arg))*matrix(f60(arg))-eye(4)), 1e-12)
        t06 = matrix([[1,0,0,3],[0,-1,0,0],[0,0,-1,-1],[0,0,0,1]])
        self.assertLess(amax(matrix(f06(zeros(10))) - t06), 1e-12)

    def test_robo_misc(self):
        self.robo = symoro.Robot.SR400()
        self.assertEqual(self.robo.chain(6), [6,5,4,3,2,1])
        self.assertEqual(self.robo.chain(6, 3), [6, 5, 4])
        self.assertEqual(self.robo.loop_chain(8, 9), [8, 9])
        self.assertEqual(self.robo.loop_chain(0, 6), [0,1,2,3,4,5,6])
        self.assertEqual(self.robo.loop_chain(6, 0), [6,5,4,3,2,1,0])
        self.assertEqual(self.robo.loop_chain(9, 10), [9,8,7,1,2,3,10])
        self.assertEqual(self.robo.get_loop_terminals(), [(9,10)])
        l1 = self.robo.get_geom_head()
        l2 = self.robo.get_dynam_head()
        l3 = self.robo.get_ext_dynam_head()
        for Name in l1[1:]+l2[1:]+l3[1:]:
            for i in xrange(self.robo.NL):
                self.robo.put_val(i, Name, var(Name + str(i)))
        for Name in l3[1:]+l2[1:]+l1[1:]:
            for i in xrange(self.robo.NL):
                v = var(Name + str(i))
                self.assertEqual(self.robo.get_val(i, Name), v)

    def test_igm(self):
        invgeom.igm_Paul(self.robo, self.symo, invgeom.T_GENERAL, 6)
        igm_f = self.symo.gen_func('IGM_gen', self.robo.get_q_vec(),
                                   invgeom.T_GENERAL)
        T = geometry.dgm(self.robo, self.symo, 0, 6,
                         fast_form=True, trig_subs=True)
        f06 = self.symo.gen_func('DGM_generated1', T, self.robo.get_q_vec())
        for x in xrange(10):
            arg = random.normal(size = 6)
            Ttest = f06(arg)
            solution = igm_f(Ttest)
            for q in solution:
                self.assertLess(amax(matrix(f06(q))-Ttest), 1e-12)

    def test_loop(self):
        self.robo = symoro.Robot.SR400()
        invgeom.loop_solve(self.robo, self.symo)
        l_solver = self.symo.gen_func('IGM_gen', self.robo.get_q_vec(),
                                      self.robo.get_q_active())
        T = geometry.dgm(self.robo, self.symo, 9, 10,
                         fast_form=True, trig_subs=True)
        t_loop = self.symo.gen_func('DGM_generated1', T, self.robo.get_q_vec())
        for x in xrange(10):
            arg = random.normal(size = 6)
            solution = l_solver(arg)
            for q in solution:
                self.assertLess(amax(matrix(t_loop(q))-eye(4)), 1e-12)

if __name__ == '__main__':
    unittest.main()
#    suite = unittest.TestSuite()
#    suite.addTest(testGeometry('test_robo_misc'))
#    unittest.TextTestRunner().run(suite)