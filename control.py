from scipy.interpolate import interp1d

import sys

#--------------------------------------------------------------------------------------------------
class Control:
    
    neq = 0
    signal = {}

    def __init__(self, reactor):
        self.input = construct_input()

    def calculate_rhs(self, reactor, t):
        rhs = []
        return rhs

    def evaluate(self, reactor, t):
        # evaluate signals
        for s in self.input['signal'] :
            if s['type'] == 'time' :
                self.signal[s['userid']] = t

        #evaluate output signals of lookup tables
        lookup_table = self.input['lookup']
        for table in lookup_table :
            insignal_name = table['x'][0]
            outsignal_name = table['f(x)'][0]
            x = table['x'][1:]
            y = table['f(x)'][1:]
            f = interp1d(x, y) #scipy function
            xnew = max(min(self.signal[insignal_name],x[-1]),x[0])
            ynew = f(xnew)
            self.signal[outsignal_name] = ynew

#--------------------------------------------------------------------------------------------------
def construct_input():
    #create dictionary inp where all input data will be stored
    inp = {}
    inp['lookup'] = [] #no default
    inp['signal'] = [] #no default
    inp['t0'] = 0 #default
    inp['t_dt'] = [] #no default
    inp['pnltime'] = '' #no default

    #read input file as a whole
    f = open('input', mode = 'r')
    s0 = f.read()
    f.close()

    #merge &-ending "line" with the next one
    s = ''
    take = True
    for c in s0 :
        if c == '&' : take = False
        if take : s += c
        if c == '\n' : take = True

    #split in lines
    lines = s.strip().split('\n')

    #remove comment-lines (*)
    lines = [x for x in lines if not x.startswith('*')]

    def convert_to_float(w) : 
        try:
            w = float(w)
        except :
            pass
        return w

    for line in lines:
        word = line.split()
        word = list(map(convert_to_float, word))

        key = word[0].lower()
        #--------------------------------------------------------------------------------------
        # just placeholder
        if key == '' :
            pass
        #--------------------------------------------------------------------------------------
        # effective delayed neutron fractions
        elif key == 'betaeff' :
            inp['betaeff'] = word[1:]
        #--------------------------------------------------------------------------------------
        # delayed neutron precursor decay time constants
        elif key == 'dnplmb' :
            inp['dnplmb'] = word[1:]
        #--------------------------------------------------------------------------------------
        # lookup table
        elif key == 'lookup' :
             lookup = {}
             lookup['x'] = word[1::2]
             lookup['f(x)'] = word[2::2]
             inp['lookup'].append(lookup)
        #--------------------------------------------------------------------------------------
        # signal varibale
        elif key == 'signal' :
             signal = {}
             signal['type'] = word[1]
             signal['userid'] = word[2]
             signal['sign'] = word[3:]
             inp['signal'].append(signal)
        #--------------------------------------------------------------------------------------
        # 
        elif key == 'solve' :
            inp['solve'] = word[1:]
        #--------------------------------------------------------------------------------------
        # integration starting time
        elif key == 't0' :
            inp['t0'] = word[1]
        #--------------------------------------------------------------------------------------
        # end of time interval and output time step for this interval
        elif key == 't_dt' :
            inp['t_dt'].append([word[1], word[2]])
        #--------------------------------------------------------------------------------------
        # prompt neutron lifetime
        elif key == 'tlife' :
            inp['tlife'] = word[1]

    # verify that t_dt present
    if inp['t_dt'] == [] :
        sys.exit('****ERROR: obligatory card t_dt specifying time_end and dtime_out is absent.')

    # verify that lookup tables use existing signals
    signal_userid = []
    for s in inp['signal'] :
        signal_userid.append(s['userid'])
    for table in inp['lookup'] :
        insignal = table['x'][0]
        outsignal = table['f(x)'][0]
        if insignal not in signal_userid :
            print('****ERROR: input signal ' + insignal + ' in lookup table ' + outsignal + ' is not defined.')
            sys.exit()
    print(inp)
    return inp
