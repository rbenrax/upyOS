:loop
clear
< "Options Menu"
< ""
< "Option 1"
< "Option 2"
< "Option 0 reload"
< ""
echo "La opcion es: " $v1
read v1 "Introduzca opcion: "
if $v1 == 1 < "Opcion 1"
if $v1 == 2 < "Opcion 2"
if $v1 != 0 goto loop
