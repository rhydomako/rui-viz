#!/usr/bin/python

from ruis import *

if __name__ == "__main__":
    
    #
    # sqlite grab file names
    #
    conn = sqlite3.connect("example.db")
    c = conn.cursor()
    c.execute("select * from example") # filenames

    rows = c.fetchall()

    ana_tokens=[]
    ana_struct={}

    #
    # grab the first row, and interprete the ntuple
    #
    for i in range(len(rows)):

        row = rows[i]
        print row

        token_name   = row[0]
        events_fname = row[1]
        rui_fname    = row[2]
        expertise    = int(row[3])
        offset       = float(row[5])

        ana = Analysis(token_name,
                       rui_fname,
                       events_fname,
                       expertise,
                       offset,
                       debug=True)

        ##
        ## bail if bad data
        ##
        if ana.data_is_good == False: continue

        ##
        ## add tags
        ##
        ana.add_tags("Avatar not in play", "red")
        ana.add_tags("PvE Combat",         "blue")
        ana.add_tags("Typed communication","green")
        ana.add_point_tag("Join group","black")

        ##
        ## Make any cuts
        ##

        ## cut pre-play
        ana.tags_times["Avatar not in play"] = [(0, ana.tags_times["Avatar not in play"][0][1])]
        
        #ana.add_cut( (0, ana.tags_times["Avatar not in play"][0][1]) )
        #ana.cut_by_tags("Typed communication")
        #cut_by_tags("PvE Combat")
        #ana.cut_all_but("PvE Combat")

        ana.apply_cuts()

        play_time = ana.calc_play_time()

        ##
        ## make data structs for 2D plot
        ##
        keys = ana.make_keys_hist()

        spaces = []
        for e in ana.events:
            if e.spt[1] == "KEY" and e.spt[2] == "SPACE" and e.cut==False:
                spaces.append(float(e.time))

        ana_tokens.append(token_name)
        ana_struct[token_name] = (keys, play_time, get_colour(expertise), spaces, ana.tags_times, ana.tags_colours, ana.events[len(ana.events)-1].time)

    
    ##
    ## Plots
    ##
    fig   = plt.figure( figsize=(12,0.4*len(ana_tokens)))
    fig_ax = fig.add_subplot(111)

    X=[]
    Y=[]
    for index, t in enumerate(ana_tokens):
        spaces = ana_struct[t][3]

        for i in spaces:
            X.append(i)
            Y.append(index)

        times   = ana_struct[t][4]
        colours = ana_struct[t][5]

        for k, v in times.items():
            print "Adding \'"+str(k)+"\' tags"
            for i in v:
                fig_ax.add_patch(mpatches.Rectangle((i[0],index-0.5),i[1]-i[0],1,fill=True, alpha=0.3,color=colours[k]))


    N = len(ana_tokens)
    ind = np.arange(N)
    
    fig_ax.set_yticks(ind)
    fig_ax.set_yticklabels(ana_tokens)
    fig_ax.set_ylim([-0.5,0.5+len(ana_tokens)-1])

    max_times = []
    for t in ana_tokens:
        max_times.append(ana_struct[t][6])
    fig_ax.set_xlim([0,max(max_times)])


    plt.subplots_adjust(left=0.1,right=0.98, top=0.90, bottom=0.3)

    fig_ax.set_xlabel('Time (s)')

    plt.scatter(X,Y, marker='.')
    plt.show()
    
