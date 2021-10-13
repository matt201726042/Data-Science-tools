def multiprocessing_func(Global, id):
    while True:
        print("a",id)
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
    Global.out = []
    processes = []

    def main():
        coreCount = 1#int(multiprocessing.cpu_count() * 0.5)
        for id in range(coreCount):
            p = multiprocessing.Process(target=multiprocessing_func, args=(Global, id))
            p.daemon = True
            processes.append(p)
        for core in range(coreCount):
            processes[core].start()
        #processes[-1].join()
    main()
    while True:
        print("b",0)
    print(Global.out)