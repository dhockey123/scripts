import numpy as np 
import matplotlib.pyplot as plt 
from matplotlib import animation
import matplotlib
matplotlib.use('TkAgg') 
fig, ax1 = plt.subplots(3)
fig.suptitle('FPU system')

########################

w = 1
dt = 0.1
alpha = 0.25
N = 16
N = N+1
x_init = np.zeros(N)
for n in range(N):
	x_init[n] = np.sin(n*np.pi / (N-1))
x = x_init 
x[-1] = 0

v_n = v = x_n  = np.zeros(N)
time = []
t = 0

modes = 8
E_list = [[] for _ in range(modes)]
PE = []
KE = []

########################
# The following three equations are taken from
# The Fermi-Pasta-Ulam "numerical experiment": history and pedagogical perspectives 	arXiv:nlin/0501053

# Returns displacement or velocity of mode m. 
# Returned value depends on whether input is array of particle displacements or velocities
def get_A(m, xv):
	A = list(map(lambda n: xv[n]*np.sin(n*m*np.pi/(N-1)), range(len(xv))))
	return sum(A)*np.sqrt(2/(N-1))

# Returns squared angular frequency of mode m
def get_W(m):
	return 4*np.sin(m*np.pi/(2*N-2))**2

# Returns energy of mode m.
# Calcs w each time its called. Not ideal. Easy fix.
def get_E(m, x, v):
	Ax = get_A(m, x)
	Av = get_A(m, v)
	w  = get_W(m)
	return (Av**2 + w*Ax**2)/2

def exact_mode_dispacement(x_init, t, m):
	ohm = 2*w*np.sin(m*np.pi/(N-1))
	tmp = np.zeros(N)
	for n in range(N-1):
		tmp[n] = x_init[n]*np.cos(2*np.pi*n*m/(N-1))*np.cos(ohm*t)
	return tmp

def leapfrog(i):
	global v_n, v, x_n, x,t, time, E_list, modes, KE, PE, x_init

	dt = 0.1
	w0 = 1
	mass = 1
	k = 1
	
	M=np.zeros(N)
	time.append(t)

	m=1
	k = get_W(m)
	ohm = 2*w0*np.sin(m*np.pi/(N-1))

	for n in range(N):
		M[n] =  (4*alpha*x_init[n]**2*w0**2 ) *np.cos(ohm*t)**2 * np.cos(k*n)**2 * (1-np.cos(k)) *np.cos(k)
	#print(M)

	v_n[1:N-1] = v[1:N-1] +  w0**2*dt*(x[2:N]-2*x[1:N-1]+x[0:N-2])*(1+alpha*(x[2:N]-x[0:N-2]))# + M[1:-1]

	PE.append(sum(list(map(lambda x: 0.5*k*x**2+(1/3)*k*x**3, x))))
	KE.append(sum(list(map(lambda v: 0.5*mass*(v**2), v))))

	
	for m in range(0, modes):
		E_list[m].append(get_E(m, x, v))
	
	axis = np.arange(0,N)
	ax1[0].clear()
	ax1[1].clear()
	ax1[2].clear()
	ax1[1].set_ylim(-1.2,1.2)
	ax1[2].set_ylim(-1.2,1.2)
	ax1[0].set_ylabel("Energy")
	ax1[0].set_xlabel("Time")
	ax1[1].set_ylabel("Displacement")
	ax1[1].set_xlabel("Particle")

	for m in range(modes):
		ax1[0].plot(time, E_list[m])
		
	x_n = x + dt*v
	v = v_n
	x = x_n

	#test = exact_mode_dispacement(x, t, 1)
	#ax1[0].plot(axis, test)
	exact_sum_of_modes = np.zeros(N)

	#########################################


	
	ax1[1].clear()
	ax1[2].clear()
	#ax1[0].set_ylim(-1.2,1.2)
	ax1[1].set_ylim(-1.2,1.2)
	ax1[2].set_ylim(-1.2,1.2)

	ax1[1].plot(axis, x)

	t += dt

	for m in range(N):
		x_mode = exact_mode_dispacement(x, t, m)
		exact_sum_of_modes += x_mode
		ax1[2].plot(axis, exact_sum_of_modes)

	##########################################

	# ax1[1].plot(axis, M)
	# ax1[2].plot(axis, x)

########################


anim = animation.FuncAnimation(fig, leapfrog,  interval  = .0001)

plt.show()
