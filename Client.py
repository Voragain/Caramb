
# -*- coding: utf-8 -*-

from Window import *
from Vector import *

class Boule:
    def __init__(self, color):
        self.size = 6
        self.position = Vector(0,0)
        self.velocity = Vector(0,0)
        self.color = color
        self.last_fixed_position = self.position
        self.last_fixed_velocity = self.velocity
        self.last_fixed_time = 0

    def getTimeToStop(self, friction):
        pass

    def getPositionAt(self, timeFrame, friction):
        pass

    def getVelocityAt(self, timeFrame, friction):
        pass


class CaramboleData:
    def __init__(self):
        self.carambole = Boule("#aa1111")
        self.blanche = Boule("#dddddd")
        self.jaune = Boule("#eeee22")
        #self.boules = [self.carambole, self.blanche, self.jaune]
        #self.carambole.position.modify(200, 300)
        #self.blanche.position.modify(000, 307)
        #self.jaune.position.modify(560, 355)
        #self.carambole.velocity.modify(200, 200)

        self.table_friction = 5
        self.ball_elasticity = 0.98
        self.ball_collision_energy_cons = 0.95
        self.wall_collision_energy_cons = 0.9

        self.boules = []
        for i in range(0, 15):
            self.boules.append(self.makeBoule(i))
        self.blanche = self.makeBlanche()
        self.boules.append(self.blanche)
        #self.red = Boule("#ee22ee")
        #self.red.position.modify(500, 300)
        #self.boules.append(self.red)

        self.fixAll()

        #self.collision(self.carambole, self.blanche)
        self.frameTime = 0
        #self.nextHit = None
        self.nextHit = self.collisionCheck()

    def start(self):
        self.blanche.velocity.modify(300, 143)
        self.frameTime = 0
        self.fixAll()
        self.nextHit = self.collisionCheck()

    def makeBlanche(self):
        b = Boule("#eeeeee")
        b.position.modify(250, 300)
        return b

    def makeBoule(self, i):
        b = Boule({0 : "#ee3333", 1 : "#33ee33", 2 : "3333ee"}[i%3])
        x = (550, 562, 562, 574, 574, 574, 586, 586, 586, 586, 598, 598, 598, 598, 598)[i]
        y = (300, 293, 307, 286, 300, 314, 279, 293, 307, 321, 272, 286, 300, 314, 328)[i]
        b.position.modify(x, y)
        return b

    def initGame(self):
        pass
        #self.blanche
        #self.carambole.position.modify()

    def partialUpdate(self, timeFrame):
        for ball in self.boules:
            bvel_len = ball.last_fixed_velocity.length()
            #print("Last fixed velocity : " + str(ball.last_fixed_velocity))
            mtime = bvel_len / self.table_friction
            #print("Time to ball stop : " + str(mtime))
            if timeFrame > mtime:
                calcTime = mtime
            else:
                calcTime = timeFrame
            fvel = Vector.Normalized(ball.last_fixed_velocity).scale(calcTime * -self.table_friction).plus(ball.last_fixed_velocity)
            avg_vel = Vector.Add(fvel, ball.last_fixed_velocity).scale(0.5)
            ball.velocity = fvel
            ball.position = Vector.Add(ball.last_fixed_position, Vector.Scaled(avg_vel, calcTime))
            
           
        # for ball in self.boules:
        #     if (ball.velocity.length_sqrd() != 0):
        #         fvel = ball.velocity.added(ball.velocity.normalized().scaled(dt * -self.table_friction))
        #         if fvel.projected(ball.velocity) < 0:
        #             fvel = Vector(0,0)
        #         avg = ball.velocity.added(fvel).scaled(0.5)
        #         ball.position = ball.position.added(avg.scaled(dt))
        #         ball.velocity = fvel

    def fixState(self, ball):
        ball.last_fixed_position = ball.position
        ball.last_fixed_velocity = ball.velocity

    def fixAll(self):
        for ball in self.boules:
            self.fixState(ball)

    def resolveCollision(self, hit):
        print("Collision at " + str(self.frameTime) + "s")
        if type(hit[2]) is Vector:
            self.wallCollision(*hit[1:])

        if type(hit[2]) is Boule:
            self.collision(*hit[1:])

    def update(self, dt):
        if self.nextHit != None:
            pass #print("Update - Next Hit " + str(self.nextHit[0]) + "/" + str(self.frameTime + dt) + "s")
        while dt > 0:
            if self.nextHit != None and self.nextHit[0] <= self.frameTime + dt:
                partialDt = self.nextHit[0] - self.frameTime
                self.frameTime += partialDt
                if partialDt > 0:
                    self.partialUpdate(self.frameTime)
                self.resolveCollision(self.nextHit)
                self.fixAll()
                self.nextHit = self.collisionCheck()
                self.frameTime = 0
                dt = dt - partialDt
            else:
                #print("TotalTime: " + str(self.totalTime) + "s")
                #print("Calculating for " + str(dt) + "s")    
                self.frameTime += dt
                self.partialUpdate(self.frameTime)
                dt = 0
        return self

    def collisionCheck(self):
        hits = []
        for i in range(0, len(self.boules)):
            res = self.firstWallTouch(self.boules[i])
            if res != None:
                hits.append(res)
            
        for i in range(0, len(self.boules)-1):
            for j in range(i+1, len(self.boules)):
                res = self.firstTouch(self.boules[i], self.boules[j])
                if res != None:
                    hits.append(res)
        

        nextHit = None
        for (time, *args) in hits:
            if nextHit == None or nextHit[0] > time:
                nextHit = (time, *args)

        if nextHit == None:
            print("No next hit")
        else:
            print("Next hit in " + str(nextHit[0]) + "s")
        return nextHit

    def firstWallTouch(self, b1):
        wallTouch = None
        if b1.velocity.x > 0:
            wallTouchX = 700 - b1.size
            wallTouchY = (wallTouchX - b1.position.x) / b1.velocity.x * b1.velocity.y + b1.position.y
            wallTouchPos = Vector(wallTouchX, wallTouchY)
            v = b1.velocity.length()
            dist = Vector.Add(wallTouchPos, Vector.Scaled(b1.position, -1)).length()
            sq = -2 * self.table_friction * dist + v*v
            if sq >= 0:
                tt = (math.sqrt(sq)-v)/-self.table_friction
                if tt >= 0:
                    print("Right side collision in " + str(tt) + "s")
                    wallTouch = (tt, b1, Vector(-1, 0), wallTouchPos)

        if b1.velocity.x < 0:
            wallTouchX = 100 + b1.size
            wallTouchY = (wallTouchX - b1.position.x) / b1.velocity.x * b1.velocity.y + b1.position.y
            wallTouchPos = Vector(wallTouchX, wallTouchY)
            v = b1.velocity.length()
            dist = Vector.Add(wallTouchPos, Vector.Scaled(b1.position, -1)).length()
            sq = -2 * self.table_friction * dist + v*v
            if sq >= 0:
                tt = (math.sqrt(sq)-v)/-self.table_friction
                if tt >= 0:
                    if wallTouch == None or wallTouch[0] > tt:
                        print("Left side collision in " + str(tt) + "s at " + str(wallTouchPos))
                        wallTouch = (tt, b1, Vector(1, 0), wallTouchPos)

        if b1.velocity.y > 0:
            wallTouchY = 450 - b1.size
            wallTouchX = (wallTouchY - b1.position.y) / b1.velocity.y * b1.velocity.x + b1.position.x
            wallTouchPos = Vector(wallTouchX, wallTouchY)
            v = b1.velocity.length()
            dist = Vector.Add(wallTouchPos, Vector.Scaled(b1.position, -1)).length()
            sq = -2 * self.table_friction * dist + v*v
            if sq >= 0:
                tt = (math.sqrt(sq)-v)/-self.table_friction
                if tt >= 0:
                    if wallTouch == None or wallTouch[0] > tt:
                        print("Top side collision in " + str(tt) + "s")
                        wallTouch = (tt, b1, Vector(0, -1), wallTouchPos)

        if b1.velocity.y < 0:
            wallTouchY = 150 + b1.size
            wallTouchX = (wallTouchY - b1.position.y) / b1.velocity.y * b1.velocity.x + b1.position.x
            wallTouchPos = Vector(wallTouchX, wallTouchY)
            v = b1.velocity.length()
            dist = Vector.Add(wallTouchPos, Vector.Scaled(b1.position, -1)).length()
            sq = -2 * self.table_friction * dist + v*v
            if sq >= 0:
                tt = (math.sqrt(sq)-v)/-self.table_friction
                if tt >= 0:
                    if wallTouch == None or wallTouch[0] > tt:
                        print("Bottom side collision in " + str(tt) + "s")
                        wallTouch = (tt, b1, Vector(0, 1), wallTouchPos)

        return wallTouch

    def firstTouch(self, b1, b2):
        #if b1.velocity.projected(b2.velocity) < 0:
        #    return None
        rm = Vector.Substract(b1.last_fixed_velocity, b2.last_fixed_velocity)
        if rm.length() == 0:
            return None
        (norm, perp) = Vector.ToNormalPerp(rm)
        direct = Vector.Substract(b2.last_fixed_position, b1.last_fixed_position)

        if Vector.Dot(rm, Vector.Normalized(direct)) < 0:
            return None

        #accel = b1_vel.normalized().scaled(-self.table_friction).added(b2_vel.normalized().scaled(-self.table_friction))
        accel = Vector.Substract(Vector.Normalized(b1.velocity).scale(-self.table_friction), 
            Vector.Normalized(b2.velocity).scale(-self.table_friction))
        ac = Vector.Dot(accel, Vector.Normalized(rm))
        #print("RM : " + str(rm))
        #print("Accel : " + str(accel))
        #print("AC : " + str(ac))

        l = Vector.Dot(direct, norm)
        d = Vector.Dot(direct, perp)

        colSize = b1.size + b2.size

        pyth = colSize*colSize - d*d
        if pyth < 0:
            return None

        a = math.sqrt(pyth)
        rl = l - a

        print("RL : " + str(rl))

        v = rm.length()
        tt = 2 * ac * rl + v*v
        if tt < 0:
            return None

        if ac == 0:
            timeToHit = rl / v
        else:            
            timeToHit = (math.sqrt(tt) - v) / ac
        if timeToHit < 0:
            return None


        #endVel = b1.velocity.added(b1.velocity.normalized().scaled(-timeToHit))
        time_to_collision = timeToHit

        collision_velocity_ball = Vector.Add(b1.velocity, Vector.Normalized(b1.velocity).scale(-time_to_collision * self.table_friction))
        average_velocity_ball = Vector.Add(b1.velocity, collision_velocity_ball).scale(0.5)
        hit_position_ball = Vector.Add(b1.position, average_velocity_ball.scale(time_to_collision))

        collision_velocity_other = Vector.Add(b2.velocity, Vector.Normalized(b2.velocity).scale(-timeToHit * self.table_friction))
        average_velocity_other = Vector.Add(b2.velocity, collision_velocity_other).scale(0.5)
        hit_position_other = Vector.Add(b2.position, average_velocity_other.scale(timeToHit))

        print("Found future collision in " + str(time_to_collision) + "s")
        print("Will happen at " + str(hit_position_ball) + " | " + str(hit_position_other))
        print("With velocity " + str(collision_velocity_ball) + " | " + str(collision_velocity_other))

        return (time_to_collision, b1, b2, hit_position_ball, collision_velocity_ball, hit_position_other, collision_velocity_other)

    def checkBallStop(self, ball):
        time_to_stop = ball.velocity.length() / self.table_friction
        if time_to_stop > 0:
            return (time_to_stop, ball)
        return None

    def relativeMovement(self, b1, b2):
        return Vector.Substract(b1.velocity, b2.velocity)

    def collision(self, b1, b2, p1, v1, p2, v2):
        print("Adjusting " + str(b1.position) + " => " + str(p1))
        print("Adjusting " + str(b2.position) + " => " + str(p2))
        b1.position = p1
        b1.velocity = v1
        b2.position = p2
        b2.velocity = v2

        (normal, perp) = Vector.ToNormalPerp(Vector.Substract(b1.position, b2.position))
        #print("Collision vector " + str(Vector.Substract(b1.position, b2.position)) + " with normal " + str(normal) + " and perp " + str(perp))
        kept1 = Vector.ProjectedOn(b1.velocity, perp)
        #given1 = Vector.ProjectedOn(b1.velocity, normal) 
        given1 = Vector.ProjectedOn(b1.velocity, normal).scale(self.ball_collision_energy_cons)
        kept2 = Vector.ProjectedOn(b2.velocity, perp)
        #given2 = Vector.ProjectedOn(b2.velocity, normal) 
        given2 = Vector.ProjectedOn(b2.velocity, normal).scale(self.ball_collision_energy_cons)

        #print("Kept : " + str(kept1))
        #print("Given : " + str(given1))
        #print("Kept : " + str(kept2))
        #print("Given : " + str(given2))

        #b1.velocity = kept1.plus(given2) 
        b1.velocity = kept1.plus(Vector.Scaled(given2, self.ball_elasticity)).plus(Vector.Scaled(given1, 1 - self.ball_elasticity))
        #b2.velocity = kept2.plus(given1) 
        b2.velocity = kept2.plus(Vector.Scaled(given1, self.ball_elasticity)).plus(Vector.Scaled(given2, 1 - self.ball_elasticity))

        #print("After collision:")
        #print("B1 : " + str(b1.position) + " -> " + str(b1.velocity))
        #print("B2 : " + str(b2.position) + " -> " + str(b2.velocity))

    def wallCollision(self, b1, w, p):
        print("Adjusting for wall " + str(b1.position) + " => " + str(p))
        b1.position = p
        (normal, perp) = Vector.ToNormalPerp(w)
        #print("Normal : " + str(normal))
        #print("Perp   : " + str(perp))

        kept1 = Vector.ProjectedOn(b1.velocity, perp)
        given1 = Vector.ProjectedOn(b1.velocity, normal)
        #print("Wall - Veloc: " + str(b1.velocity))
        #print("Wall - Kept : " + str(kept1))
        #print("Wall - Given: " + str(given1))
        #print("Wall - Taken: " + str(Vector.Scaled(given1, -1)))
        b1.velocity = Vector.Add(kept1, given1.scale(-1 * self.wall_collision_energy_cons))

    def getBoules(self):
        return map(lambda b: (b.position, b.color, b.size), self.boules)


cd = CaramboleData()
cw = CaramboleWindow()

pyglet.clock.schedule_interval(lambda dt: cw.reflectModel(cd.update(dt)), 1/120.0)
pyglet.app.run()
