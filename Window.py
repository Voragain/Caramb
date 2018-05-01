
# -*- coding: utf-8 -*-

import pyglet
import math

from functools import reduce
from pyglet.gl import *
from HLSL import *

from Vector import *

class CaramboleWindow(pyglet.window.Window):
    def __init__(self):
        config = Config(sample_buffers=1, samples=4,
                    depth_size=16, double_buffer=True)
        super(CaramboleWindow, self).__init__(800, 600, config=config)
        self.field = pyglet.graphics.vertex_list(4, 
             ('v2i', (100, 150, 700, 150, 100, 450, 700, 450)),
             ('c3f', (0.2, 0.5, 0.2, 0.2, 0.5, 0.2, 0.2, 0.5, 0.2, 0.2, 0.5, 0.2))
        )
        self.border = pyglet.graphics.vertex_list(10,
            ('v2i', (90, 140, 100, 150, 710, 140, 700, 150, 710, 460, 700, 450, 90, 460, 100, 450, 90, 140, 100, 150)),
            ('c3f', (0.25, 0.2, 0.2) * 10)
        )
        self.ball = pyglet.graphics.vertex_list(22,
            ('v2f', (0,0) + reduce(lambda a, b: a+b, map(lambda x: (math.cos(x), math.sin(x)), map(lambda x: x/20 * math.pi*2, range(21))))),
            ('c3f', (1,1,1) * 22)
        )

        self.cue = pyglet.graphics.vertex_list(4,
            ('v2f', (0, -2, 100, -2.5, 0, 2, 100, 2.5)),
            ('c3f', (0, 0, 0) * 4),
            ('0t2f', (0, 0, 0, 0, 1, 0, 1, 0))
        )

        ballShaderCode = """
            in vec4 gl_FragCoord; 
            uniform vec3 color;
            uniform vec2 center;
            uniform float size;
            uniform vec3 lightPosition = vec3(300, 200, 600);
            uniform vec3 lightDiffuseColor = vec3(1.0, 1.0, 1.0);
            uniform vec3 lightSpecularColor = vec3(1.0, 1.0, 1.0);

            void main()
            {
                float dist = distance(center, gl_FragCoord.xy) / size;
                float z = sqrt(1.0 - dist*dist);
                vec3 pos = vec3(gl_FragCoord.xy, z*size);
                vec3 normal = normalize(vec3(gl_FragCoord.xy - center, z*size));

                vec3 lightRay = normalize(lightPosition - pos);
                float light = abs(dot(lightRay, normal));
                float spec = max(0, light - 0.9) * 15.0;
                spec = spec * spec;

                //gl_FragColor = vec4(z, z, z, 1.0);

                vec3 col = light * color * (1-spec) + spec * lightSpecularColor;
                //col = vec3(spec, spec, spec);

                gl_FragColor = vec4(col, 1.0);
            }
        """

        cueVertexShaderCode = """
            varying float vDist;

            void main(void)
            {
                vDist = gl_MultiTexCoord0.s;
                gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
            }
        """

        cueVertexFragmentCode = """
            varying float vDist;
            uniform vec3 lightPosition = vec3(300, 200, 300);
            uniform vec2 cueNormal = vec2(1,0);
            uniform vec2 cueMid = ()

            void main(void)
            {
                float c = 2 * abs(0.5 - vDist);
                float z = sqrt(1.0 - c*c);
                vec3 normal = 
                gl_FragColor = vec4(c, 0, 0, 1);
            }
        """

        self.ballShader = Shader("", ballShaderCode)
        #self.cueShader = Shader(cueVertexShaderCode, cueVertexFragmentCode)
        #self.cueShader = Shader("", cueVertexFragmentCode)
        self.boules = []
        self.hasHit = False
        self.hitVec = None
        self.gameActive = False
        self.mousePos = None
        self.hitForce = 0
        self.pressed = False
        

    def reflectModel(self, model, dt):
        self.boules = model.getBoules()
        self.blanchePos = model.getBlanchePos()
        self.gameActive = model.gameActive
        if self.pressed:
            self.hitForce += dt

        if self.hasHit:
            if self.hitForce > 0:
                self.hitForce = max(0, self.hitForce - dt * 40)
            if self.hitForce == 0:
                model.hitBall(self.hitVec.scale(4))
                self.hasHit = False
                self.hitVec = None
                
        #print("reflectModel")

    def on_mouse_motion(self, x, y, dx, dy):
        self.mousePos = Vector(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        self.pressed = True

    def on_mouse_release(self, x, y, button, modifiers):
        self.pressed = False
        self.hasHit = True
        scale = min(self.hitForce * self.hitForce * 40, 250)
        self.hitVec = Vector.Substract(self.blanchePos, Vector(x,y)).normalize().scale(scale)
        
    def on_draw(self):
        glClearColor(0.8, 0.8, 0.8, 1)
        self.clear()
        glLoadIdentity()

        #self.ballShader.bind()
        self.field.draw(GL_TRIANGLE_STRIP)
        #self.ballShader.unbind()

        self.border.draw(GL_TRIANGLE_STRIP)


        self.ballShader.bind()

        for (pos, col, size) in self.boules:
            glLoadIdentity()
            rgb = tuple(int(col.strip("#")[i:i+2], 16)/256 for i in (0, 2 ,4))
            self.ballShader.uniformf("color", *rgb)
            self.ballShader.uniformf("center", pos.x, pos.y)
            self.ballShader.uniformf("size", size)
            glTranslatef(pos.x, pos.y, 0)
            glScalef(size, size, 1.0)
            self.ball.draw(GL_TRIANGLE_FAN)

        self.ballShader.unbind()

        glLoadIdentity()

        if not self.gameActive:
            label = pyglet.text.Label("PLAY!", font_size = 24, x = self.width/2, y = 500, anchor_x = 'center', color = (0, 0, 0, 255))
            label.draw()

        if not self.gameActive and self.mousePos != None:
            glTranslatef(self.blanchePos.x, self.blanchePos.y, 0)
            glRotatef(Vector.Substract(self.mousePos, self.blanchePos).angle_deg(), 0, 0, 1.0)
            scale = min(self.hitForce * self.hitForce * 40, 250)
            scale = scale / 3.0
            glTranslatef(7 + scale, 0, 0)

            self.cue.draw(GL_TRIANGLE_STRIP)

            #self.drawVectorAt(Vector.Substract(self.blanchePos, self.mousePos).scale(2), self.blanchePos.x, self.blanchePos.y, 2.5)

        glLoadIdentity()

        # glColor4f(0,0,0,1)
        
        # v = Vector(50, 50)

        # self.drawVectorAt(v, 50, 50, 2)
        # self.drawVectorAsLine(v.rotated90cw(), 50, 50, 15)

    def drawVectorAt(self, v, x, y, w):
        (front, right) = Vector.ToNormalPerp(v)
        len = v.length()
        glBegin(GL_TRIANGLES)
        #print("Vec : " + str(front.__dict__))
        glVertex3f(x + front.x * len, y + front.y * len, 0)
        glVertex3f(x + right.x * w, y + right.y * w, 0)
        glVertex3f(x - right.x * w, y - right.y * w, 0)
        glEnd()

    def drawVectorAsLine(self, v, x, y, l):
        (front, right) = v.get_directions()
        glBegin(GL_LINES)
        #print("Vec : " + str(front.__dict__))
        glVertex3f(x + front.x * l, y + front.y * l, 0)
        glVertex3f(x + front.x * -l, y + front.y * -l, 0)
        glEnd()
