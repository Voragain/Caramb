
# -*- coding: utf-8 -*-

import pyglet
import math

from functools import reduce
from pyglet.gl import *
from HLSL import *

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
            ('v2f', (0, 0, 100, -2, 0, 5, 100, 7)),
            ('c3f', (0, 0, 0) * 4),
            ('0t2f', (0, 0, 0, 0, 1, 0, 1, 0))
        )

        ballShaderCode = """
            in vec4 gl_FragCoord; 
            uniform vec3 color;
            uniform vec2 center;
            uniform float size;
            uniform vec3 lightPosition = vec3(300, 200, 300);
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
                float spec = max(0, light - 0.9) * 20.0;

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
        self.start = False
        self.started = False
        

    def reflectModel(self, model):
        if self.start:
            model.start()
            self.start = False
        self.boules = model.getBoules()
        #print("reflectModel")

    def on_mouse_press(self, x, y, button, modifiers):
        if self.started == False:
            self.start = True
            self.started = True

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

        # glColor4f(0,0,0,1)
        
        # v = Vector(50, 50)

        # self.drawVectorAt(v, 50, 50, 2)
        # self.drawVectorAsLine(v.rotated90cw(), 50, 50, 15)

    def drawVectorAt(self, v, x, y, w):
        (front, right) = v.get_directions()
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
