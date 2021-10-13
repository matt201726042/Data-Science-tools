import time
def multiprocessing_func(Global, id):
    i = 0
    while True:
        i += 1.1
        for j in range(10000000):
            i += 0.00000001
        Global.out = i
    out = Global.out
    out.append(id)
    Global.out = out

if __name__ == '__main__':
    import multiprocessing
    from multiprocessing import Process
        
    manager = multiprocessing.Manager()
    global Global
    global processes
    Global = manager.Namespace()
    Global.out = 0
    processes = []

    coreCount = 1#int(multiprocessing.cpu_count() * 0.5)
    for id in range(coreCount):
        p = multiprocessing.Process(target=multiprocessing_func, args=(Global, id))
        p.daemon = True
        processes.append(p)
    for core in range(coreCount):
        processes[core].start()
    #processes[-1].join()
    while True:
        print("b",Global.out)