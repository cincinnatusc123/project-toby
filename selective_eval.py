import globles

scaling =0 

#fin = open("noshow_4-round.csv")
def nodeFile2Interesting( filepath ) :
    assert '/' in filepath
    [path,filename] = filepath.rsplit('/',1)
    [name,ext] = filename.rsplit('.',1)
    fin = open(filepath)
    fout = open( "%s/%s_interesting.%s" % (path,name,ext), 'w' )
    for line in fin.readlines() :
        splt = line.strip().split(',')
        postflop_actions = [int(splt[node]) for node in [5,8,11]]
        #print postflop_actions
        num_kkdd = sum( [act==3 for act in postflop_actions] )
        if num_kkdd < 3 :
           fout.write( "%s" % line )

    fout.close()
    fin.close()

#examine some particular subset of nodes, and return a dictionary of:
#values_nodes_take_on : frequency in file
def computeTypeFrequencies( focus_cols, given_cols=[], given_conditions=[''] ) :
    fin_test = open(globles.TRAIN_FILENAME)
    value_counts = {}
    n_not_excluded = 0
    for line_num,line in enumerate(fin_test.readlines()) :
        splt = line.strip().split(",")
        given_values = ','.join( [splt[i] for i in given_cols] )
        #print given_values
        if not given_values in given_conditions :
            continue

        #print line
        n_not_excluded += 1
        try :
            value = ','.join( [splt[i] for i in focus_cols] )

            if value in value_counts :
                value_counts[value] += 1
            else :
                value_counts[value] = 1
        except Exception as e:
            print str(e)
            print line
            print line_num,splt

    for value in value_counts :
        value_counts[value] = value_counts[value] / float(n_not_excluded)

    #print 'n_not_excluded', n_not_excluded
    return value_counts


def returnMasker( focus_nodes, ignore_set ) :
    def inner( line_splt ) :
        value = ','.join( [line_splt[i] for i in focus_nodes] )
        return value in ignore_set
    return inner

    
if __name__ == '__main__' :

    nodeFile2Interesting("nodes/all_hyper_sartre_4-round_training_showdown.csv") 

    #type_freqs =  computeTypeFrequencies( [4] )
    #svalues = sorted( type_freqs.keys(), key=lambda k : k ) #type_freqs[k] )
    #s = 0
    #for v in svalues :
        #s += type_freqs[v]
        #print v, "\t" , type_freqs[v]
    #print "sum", s
    #print len(svalues), "present values"
    #assert False
#
    #given_cols = []
    #given_conditions = ['']
    #priors = []
    #for node in range(24) :
        #if node in [2,3,4,5,8,9,10,11,14,15,16,17,20,21,22,23] :
            #type_freqs =  computeTypeFrequencies( [node], given_cols, given_conditions )
           # 
            ###find the scaling factor, such that the new example file is about the
            ###same size as before
            ##amts = type_freqs.keys()
            ##percs = type_freqs.values()
#
            ##for i in range(2,5) :
                ##scaled_amts = [float(amt)/i for amt in amts]
                ##print i
                ##scaled_percs = [float(percs[j]) * scaled_amts[j] for j in range(len(percs))]
                ##print "i:",i, sum(scaled_percs)
#
            #pprobs = []
            #for a in range(1,13) :
                #a = str(a)
                #if a in type_freqs :
                    #p = str(type_freqs[a])
                #else :
                    #p = '0'
                #pprobs.append(p)
            #priors.append( '['+','.join( pprobs )+']' )
        #else :
            #priors.append( '[42,42,42,42,42,42,42,42,42,42,42,42]' )
#
    #print '['+';'.join(priors)+']'
   # 
   ### 
