import time
import subprocess
import os
import pylab
import numpy

if __name__ =='__main__':

  try:
    hiddencube_home = os.environ['HIDDENCUBE_HOME']
    image_num = 2000

    times = range(0,9)

    for para in range(1, 10):
      #para , rotations 

      cmd = hiddencube_home + "/run_param.sh {0} {1}".format(para, image_num)

      ret = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read();

      print ret

      for line in ret.split():
        if line[0].isdigit():
          times[para-1] = float(line)


    print times

    fig = pylab.figure()
    x = range(1,10)
    y = times
    pylab.plot(x,y)
    pylab.xlabel("Parallelization Factor")
    pylab.ylabel("Execution Time in Seconds")
    pylab.title("Execution Time Generating {0} Images vs Parallelization Factor".format(image_num))
    pylab.savefig(hiddencube_home + '/benchmark/para_vs_executiontime.png')
    pylab.close(fig)



  except KeyError:
    print "\t ERROR: You need to set the HIDDENCUBE_HOME environment variable to the path to the home directory of this project.  Execute a command similar to 'export HIDDENCUBE_HOME=/home/ncarey/gitrepos/HiddenCubeDataset'"

    #print "Total: {0}".format(times[0])
#    print "Total: {0}".format(times[-1] - times[0])
#    print "Start Set: {0}".format(times[1] - times[0])
#    print "Sim Set: {0}".format(times[2] - times[1])
#    print "RandRots: {0}".format(times[3] - times[2])
#    print "Color: {0}".format(times[4] - times[3])

#
