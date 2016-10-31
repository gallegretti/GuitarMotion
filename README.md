# GuitarMotion

Alunos:  
* Gabriel Allegretti   
* Carlos Francisco Pinheiro    

Professor:
* Anderson Maciel    

## \HOST

Características:
* Roda em windows + python 3.x

Responsável por:
* Conectar com clientes
* Receber comandos dos clientes
* Decidir a mudança de tom

## \ANDROID_CLIENT

Características:
* Roda em android

Resposável por:
* Conectar com um host
* Detectar movimentos pré-definidos e associar ao comando correspondente
* Enviar o comando ao host

### Dados comuns entre os projetos:

Comandos
```
COMMAND_NONE          = 0x00
COMMAND_JOLT_UP       = 0x01
COMMAND_JOLT_DOWN     = 0x02
COMMAND_NECK_UP       = 0x03
COMMAND_NECK_STRAIGHT = 0x04
COMMAND_NECK_DOWN     = 0x05
```

UID do bluetooth
```
"5E66F20D-7079-472C-B8C3-97221B7C67F7"
```
