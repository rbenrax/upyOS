clear
:loop
< "Opcion 1"
< "Opcion 2"
< "Opcion 0"
< ""
echo "La opcion es: " $v1
read v1 "Introduzca opcion: "
if $v1 == 1 < "Opcion 1"
if $v1 == 2 < "Opcion 2"
if $v1 != 0 goto loop
