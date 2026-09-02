"""Mutadores de medidas por autor, para que «de quién es cada uno» sea un dato y no una nota.

`nucleo/mutacion.py` trae los que escribió quien diseñó el lenguaje. Ese conjunto tiene un problema
que ningún número puede mostrar desde adentro: **un mutador que nadie escribió no puede producir un
sobreviviente**, así que «todos muertos» mide cobertura sobre un espacio de autoría propia.

Acá viven los de otros autores, cada uno con su `PROCEDENCIA.md` declarando qué vio y qué no. Esa
declaración es el artefacto; el código sin ella no dice nada, porque desde afuera un mutador escrito
mirando la implementación y uno escrito a ciegas se ven igual.
"""
