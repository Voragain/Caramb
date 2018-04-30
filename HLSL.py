
# -*- coding: utf-8 -*-

import ctypes as c
from pyglet.gl import *

class Shader:
    def __init__(self, vertex, fragment):
        self.handle = glCreateProgram()

        self.compileShader(vertex, GL_VERTEX_SHADER)
        self.compileShader(fragment, GL_FRAGMENT_SHADER)
        self.linkShaders()

    def compileShader(self, shaderCode, shaderType):
        if shaderCode == "":
            return
        buff = c.create_string_buffer(shaderCode.encode("utf-8"))
        c_text =  c.cast(c.pointer(c.pointer(buff)), c.POINTER(c.POINTER(GLchar)))
        shader = glCreateShader(shaderType) 
        glShaderSource(shader, 1, c_text, None)
        glCompileShader(shader) 
        rcode = c.c_int(0) 
        glGetShaderiv(shader, GL_COMPILE_STATUS, c.byref(rcode)) 
        if not rcode: 
            print("Error compiling shader " + str(shaderType))
        else: 
            glAttachShader(self.handle, shader); 
            
    def linkShaders(self): 
        glLinkProgram(self.handle) 
        rcode = c. c_int(0) 
        glGetProgramiv(self.handle, GL_LINK_STATUS, c.byref(rcode)) 
        if not rcode: 
            print("Error linking shaders")
        else: 
            self.linked = True 
            
    def bind(self): 
        glUseProgram(self.handle) 
    
    def unbind(self): 
        glUseProgram(0) 

    def uniformf(self, name, *vals): 
        c_name = c.create_string_buffer(name.encode("utf-8"))
        gl_name =  c.cast(c.pointer(c_name), c.POINTER(GLchar))
        uloc = glGetUniformLocation(self.handle, gl_name)
        if len(vals) == 1: 
            glUniform1f(uloc, *vals)
        elif len(vals) == 2: 
            glUniform2f(uloc, *vals)
        elif len(vals) == 3: 
            glUniform3f(uloc, *vals)
        elif len(vals) == 4: 
            glUniform4f(uloc, *vals)
        else:
            print("Error - uniformf can take at most 4 arguments")
