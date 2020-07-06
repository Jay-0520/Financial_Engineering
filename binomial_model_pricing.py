import math


class Calpriceby_binomial_tree(object):
    '''
    Here we use binomial lattice model to price fixed income derivatives
    
  

    '''

    def __init__(self, inital_rate, period_lim):

        self.R0 = inital_rate
        self.n = period_lim;

        # stonk movement rate u (1/u = d)
        # and risk free probabilities calibrated for black-scholes model
        self.u = 1.1; self.d = 0.9; self.q = 0.5

    def ZCB_value(self, Cu, Cd, rate, coupon):
        '''
        compute the price of zero-coupon bond 
        '''
        return coupon + (1/(1+rate))*(Cu*self.q + Cd*(1-self.q));
    
    def forward_value(self, Cu, Cd, rate):
        '''
        compute the price of a forward contract 
        '''    
    
        return (1/(1+rate))*(Cu*self.q + Cd*(1-self.q));
    
    def option_value(self, Cu, Cd, rate):
        '''
        compute the price of an option 
        '''        
        return (1/(1+rate))*(Cu*self.q + Cd*(1-self.q));

    def future_value(self, Cu, Cd):
        '''
        compute the price of a future 
        '''   
        return Cu*self.q + Cd*(1-self.q);
    
    def swap_value(self, Cu, Cd, rate, fix_rate):
        '''
        compute the price of a swap 
        '''  
        return (1/(1+rate))*((rate-fix_rate)+Cu*self.q + Cd*(1-self.q));

    def make_s_rate_lattice(self):
        '''
        construct a short rate lattice
        ''' 
        # initialize the lattice
        rate_lattice = {"t="+str(i):[] for i in range(self.n+1)}

        for k in range(0, self.n+1):
            for j in range(k+1):
                rate = self.R0*(self.u**(k-j))*(self.d**j);
                rate_lattice["t="+str(k)].append(round(rate,4));
        return rate_lattice

    def make_ZCB_lattice(self, lattice, mature_date, facevalue, coupon):
        l = mature_date

        ZCB_lattice              = {"t="+str(i):[] for i in range(self.n+1)}
        ZCB_lattice["t="+str(l)] = [facevalue+coupon]*(l+1)

        while(l>0):
            for s in range(l):
                Cu = ZCB_lattice["t="+str(l)][s]
                Cd = ZCB_lattice["t="+str(l)][s+1]
                rate = lattice["t="+str(l-1)][s]

                ZCB_value = self.ZCB_value(Cu, Cd, rate,coupon);
                ZCB_lattice["t="+str(l-1)].append(round(ZCB_value,4))
            l-=1;
        return ZCB_lattice;
    
    def make_forward_lattice(self, lattice, r_lattice, mature_date, coupon):
        l = mature_date;

        forward_lattice              = {"t="+str(i):[] for i in range(self.n+1)}
        forward_lattice["t="+str(l)] = [i - coupon for i in lattice["t="+str(l)]] 
      
        while(l>0):
            for s in range(l):
                Cu = forward_lattice["t="+str(l)][s]
                Cd = forward_lattice["t="+str(l)][s+1]
                rate = r_lattice["t="+str(l-1)][s]

                forward_value = self.forward_value(Cu, Cd, rate);
                forward_lattice["t="+str(l-1)].append(round(forward_value,4))
            l-=1;
        return forward_lattice;
    
    def make_future_lattice(self, lattice, r_lattice, mature_date, coupon):
        l = mature_date;

        future_lattice              = {"t="+str(i):[] for i in range(self.n+1)}
        future_lattice["t="+str(l)] = [i-coupon for i in lattice["t="+str(l)]] 

        while(l>0):
            for s in range(l):
                Cu = future_lattice["t="+str(l)][s]
                Cd = future_lattice["t="+str(l)][s+1]
                rate = r_lattice["t="+str(l-1)][s]

                future_value = self.future_value(Cu, Cd);
                future_lattice["t="+str(l-1)].append(round(future_value,4))
            l-=1;
        return future_lattice;
    
    
    def make_options_lattice(self, lattice, r_lattice, mature_date, coupon, strike, is_call,is_american):
        early_ex = mature_date; l = mature_date;
        t = 1;
        if not is_call: t*=-1;

        option_lattice              = {"t="+str(i):[] for i in range(self.n+1)}
        option_lattice["t="+str(l)] = [max(round(t*(i-strike),4), 0) for i in lattice["t="+str(l)] ]
        print option_lattice

        while(l>0):
            for s in range(l):
                Cu = option_lattice["t="+str(l)][s]
                Cd = option_lattice["t="+str(l)][s+1]
                rate = r_lattice["t="+str(l-1)][s]
                
                strike_dif = t*(lattice["t="+str(l-1)][s]-strike)
                option_price = self.option_value(Cu, Cd, rate)

                if is_american and (strike_dif>option_price) and (l-1<early_ex):
                    early_ex = l-1;
                    option_price = self.option_value(Cu, Cd, rate)

                option = max(strike_dif, option_price)
                option_lattice["t="+str(l-1)].append(round(option,4))

            l-=1;

        return option_lattice;
    
    
    def make_swap_lattice(self, r_lattice, mature_date, begin_date,  fix_rate):
        l = mature_date;
        t = begin_date;

        swap_lattice              = {"t="+str(i):[] for i in range(self.n+1)}
        swap_lattice["t="+str(l)] = [round((i-fix_rate) / (1+i),8) for i in r_lattice["t="+str(l)]] 
      
        while(l>0):
            for s in range(l):
                Cu = swap_lattice["t="+str(l)][s]
                Cd = swap_lattice["t="+str(l)][s+1]
                rate = r_lattice["t="+str(l-1)][s]

                if l-1 < t:
                    swap_value = (1/(1+rate))*(Cu*self.q + Cd*(1-self.q));
                else:
                    swap_value = self.swap_value(Cu, Cd, rate, fix_rate);
                    
                swap_lattice["t="+str(l-1)].append(round(swap_value,8))
                
            l-=1;
        return swap_lattice;
    

    def make_swaption_lattice(self, lattice, r_lattice, mature_date, begin_date, strike):
        l = mature_date;
        t = begin_date;

        swap_lattice              = {"t="+str(i):[] for i in range(self.n+1)}
        swap_lattice["t="+str(l)] = [max((i-strike), 0)for i in lattice["t="+str(l)] ]
      
        while(l>0):
            for s in range(l):
                Cu = swap_lattice["t="+str(l)][s]
                Cd = swap_lattice["t="+str(l)][s+1]
                rate = r_lattice["t="+str(l-1)][s]

                swap_value = (1/(1+rate))*(Cu*self.q + Cd*(1-self.q));
                    
                swap_lattice["t="+str(l-1)].append(round(swap_value,8))
                
            l-=1;
        return swap_lattice;

if __name__ == "__main__":
    
    # init the tree with parameters
    t = Calpriceby_binomial_tree(
                   inital_rate = 0.05,
                   period_lim = 10);
    
    # first, generate the short rate lattice from which we can answer the following
    # quiz questions
    s_rate_lattice = t.make_s_rate_lattice()

    print s_rate_lattice


    # question 1  - 61.6193
    # Compute the price of a zero-coupon bond (ZCB) that matures at time t = 10 
    # and that has face value 100.
    ZCB_lattice = t.make_ZCB_lattice(s_rate_lattice, mature_date=10, facevalue=100, coupon=0)
    ZCB_lattice_short = t.make_ZCB_lattice(s_rate_lattice, mature_date=4, facevalue=100, coupon=0)
    ZCB_price = ZCB_lattice["t=0"];
    print ZCB_price


    # question 2
    # Compute the price of a forward contract on the same ZCB of the previous 
    # question where the forward contract matures at time t = 4.
    
    forward_lattice = t.make_forward_lattice(ZCB_lattice, s_rate_lattice, mature_date=4, coupon=0)
    forward_price = forward_lattice["t=0"];
    print forward_price
    print (forward_price[0]*100)/ZCB_lattice_short["t=0"][0] # 82.285we need to get 82.285
    
 
    # question 3 - 74.825
    # Compute the initial price of a futures contract on the same ZCB of the previous 
    # two questions. The futures contract has an expiration of t = 4t=4.
    
    future_lattice = t.make_future_lattice(ZCB_lattice,s_rate_lattice, mature_date=4, coupon=0)
    future_price = future_lattice["t=0"];
    print future_price 
        
        
    # question 4 - 2.357
    # Compute the price of an American call option on the same ZCB of the previous three questions. 
    # The option has expiration t = 6  and strike = 80.
    option_lattice = t.make_options_lattice(ZCB_lattice, s_rate_lattice,  mature_date=6, coupon=0, strike=80, \
                                           is_call=True, is_american=True)
    option_price = option_lattice["t=0"];
    print option_price
    

    # question 5
    #Compute the initial value of a forward-starting swap that begins at t=1, with maturity t = 10 
    # and a fixed rate of 4.5%. (The first payment then takes place at t = 2 and the final payment 
    # takes place at t = 11 as we are assuming, as usual, that payments take place in arrears.) 
    # You should assume a swap notional of 1 million and assume that you receive floating and pay fixed.)
    
    swap_lattice = t.make_swap_lattice(s_rate_lattice, mature_date=10, begin_date=1, fix_rate=0.045)
    
    # begins at t=1,
    swap_price= swap_lattice["t=0"];
    print swap_price[0]*1000000 

    # question 6
    # Compute the initial price of a swaption that matures at time t = 5  and has a strike of 0. The underlying 
    # swap is the same swap as described in the previous question with a notional of 1 million. To be clear, 
    # you should assume that if the swaption is exercised at t = 5 then the owner of the swaption will receive 
    # all cash-flows from the underlying swap from times t = 6t=6 to t = 11t=11 inclusive. (The swaption strike 
    # of 0 should also not be confused with the fixed rate of 4.5% on the underlying swap.)
    
    swaption_lattice = t.make_swaption_lattice(swap_lattice,s_rate_lattice, mature_date=5, begin_date=1, strike=0)
    # begins at t=1,
    swaption_price= swaption_lattice["t=0"];
    print swaption_price[0]*1000000
    
    
    
