set terminal svg font '/usr/share/fonts/dejavu/DejaVuSans.ttf'

set output "fade.svg"
#set title "Usage" 
set xlabel "Čas [ms]"
set ylabel "Hlasitosť [%]"
#set yrange [0:9]
#set xrange [0:100]
#set xtics (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
#set ytics (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
set grid
plot "fade.dat" with linespoints title "Pieseň 1", \
        "fade2.dat" with linespoints title "Pieseň 2"
unset output
