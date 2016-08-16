# Shader Viewer

Für das Modul Generative Computergrafik an der Hochschule RheinMain wurde ein OpenGL-Programm implementiert, welches vollständig ohne fixed-function Funktionalität
auskommen soll.
- ein texturiertes Modell, welches als obj-File mit mtlFile und passender Textur gespeichert ist, soll eingelesen und dargestellt werden
- über folgende Tasten sind Änderungen am Modell möglich
 - **T** Texturen an und ausschalten
 - **S** Darstellungsart Solid (gefüllt)
 - **W** Darstellungsart Wireframe (Drahtgittermodell)
 - **P** Darstellungsart Points (Punkte)

# Anleitung
Es wurden zwei Shader Viewer implementiert.
- simpleShaderViewer.py für ein einzelnes Modell
- multiShaderViewer.py für zwei Modell (Umschalten mit 1 und 2)

Zum ausführen können folgende Kommandos genutzt werden:
````
python simpleShaderViewer.py objectfile.obj
python multiShaderViewer.py objectfile.obj objectfile.obj
````

# Screenshot
![Screenshot](https://github.com/HenryVogt/Shader_Viewer/blob/master/images/deadpool.PNG)

