from Fifa14Client import LoginManager
from Fifa14Client import WebAppFunctioner
import time
import random
import ConfigParser
from extra import EAHash

def step(current):
    if current <=9900:
        newstep = current+100
    else:
        newstep = current+250
    return newstep;
    
def priceadjust(arbitrary_price):
    if arbitrary_price<10000:
        return int(arbitrary_price/100)*100;
    else:
        return int(arbitrary_price/250)*250;

    
def do_main():
    global bought_num
    global sold_num
    Config = ConfigParser.ConfigParser()
    Player = ConfigParser.ConfigParser()
    Pricefactor = ConfigParser.ConfigParser()
    Config.read("accounts_example.ini")
    Player.read("player_data.ini")
    Pricefactor.read("factors.ini")
    for factor in Pricefactor.sections():
        bidfactor = float(Pricefactor.get(factor,'bidfactor'))
        listfactor = float(Pricefactor.get(factor,'listfactor'))
    
    try:
        for section in Config.sections():
            email = Config.get(section, 'Email')
            password = Config.get(section, 'Password')
            secret_answer = Config.get(section, 'Secret')
            security_hash = EAHash.EAHashingAlgorithm().EAHash(secret_answer)
            platform = Config.get(section, 'Platform')

            login = LoginManager.LoginManager(email,password,security_hash,platform)
            login.login()
            func = WebAppFunctioner.WebAppFunctioner(login)
            func = WebAppFunctioner.WebAppFunctioner(login)
            print "This is a newwwwwwwwwwwww round!!!!!! For the %s" %section
            print "Checking the coins amount:"
            coins=func.get_coin_amount()
            print(coins)
            
            watchlist_max = 30
                    
            #checking watchlist and tradepile
            try:
                watch_item=func.get_watchlist()
                print "Looking at watchlist now!"
                watch_item_len=len(watch_item)
                print ("%s items in watchlist..." % watch_item_len)
                for item in watch_item:
                    if item.tradeState == 'closed':
                        if item.bidState != 'highest':
                            func.remove_card_from_watchlist(item)
                            print 'removed one item from watchlist'
                            watch_item_len = watch_item_len - 1
                        time.sleep(1)
            except KeyError:
                pass
            
            try:
                trade_item=func.get_tradepile()
                print "Updating trade pile now!"
                trade_list_len=len(trade_item)
                print ("%s items in trade pile..." % trade_list_len)
                for item in trade_item:
                    if item.tradeState =='closed':
                        print "removing 1 sold item"
                        trade_list_len=trade_list_len-1
                        try:
                            func.remove_from_tradepile(item)
                        except ValueError:
                            pass
            except KeyError:
                pass
            
            #search, bid, move, and list all players in player_data.ini
            for player in Player.sections():
                playername = Player.get(player, 'Name')
                playerID = int(Player.get(player, 'ID'))
                playerprice = float(Player.get(player, 'MarketPrice'))
                Player_bidprice = priceadjust(playerprice*bidfactor)
                player_listprice = priceadjust(playerprice*listfactor)
                
                try:
                    print ("Searching for %s with price %d now!" % (playername,Player_bidprice))
                    bidding_player = func.search(num=48, macr=Player_bidprice, maskedDefId=playerID)
                    qualified_num = len(bidding_player)
                    print ("Found %s qualified %s!" % (qualified_num, playername))
                    for item in bidding_player:
                        actualBid = max(item.currentBid, item.startingBid)
                        wanttobid = step(Player_bidprice)
                        if item.expires <1100 and watch_item_len<watchlist_max:
                            if actualBid<Player_bidprice:
                                if item.bidState != 'highest' and coins-Player_bidprice>500:
                                    print 'prepare to bid a %s at %s' %(playername, wanttobid)
                                    try:
                                        func.bid(item, wanttobid)
                                        coins = coins-wanttobid
                                        print 'just bid one %s at %s, available coins: %s' %(playername, wanttobid, coins)
                                    except:
                                        pass
                                    time.sleep(1)
                except:
                    pass
                
                try:
                    watch_item=func.get_watchlist()
                    print "Looking at watchlist now!"
                    watch_item_len=len(watch_item)
                    print ("%s items in watchlist..." % watch_item_len)
                    for item in watch_item:
                        if item.tradeState == 'closed':
                            if item.bidState == 'highest':
                                if trade_list_len<80:
                                    func.move(item, 'trade')
                                    trade_list_len=trade_list_len+1
                                    bought_num = bought +1
                                    print 'moved one item to tradepile'
                        elif item.bidState!='highest':
                            func.remove_card_from_watchlist(item)
                            print 'removed one item from watchlist'
                        time.sleep(1)
                except KeyError:
                    pass
                
                
                try:
                    trade_item=func.get_tradepile()
                    print "Updating trade pile now!"
                    trade_list_len=len(trade_item)
                    print ("%s items in trade pile..." % trade_list_len)
                    for item in trade_item:
                        if item.tradeState == 'expired' or item.tradeState == None:
                            if item.assetId == playerID:
                                func.list_card(item,player_listprice,step(player_listprice),3600)
                                time.sleep(1)
                                print ("listed one %s at %s" %(playername, player_listprice))
                        elif item.tradeState =='closed':
                            sold_num= sold_num +1
                            print "removing 1 sold item"
                            trade_list_len=trade_list_len-1
                            try:
                                func.remove_from_tradepile(item)
                            except ValueError:
                                pass
                except KeyError:
                    pass

    except:
        pass
    #sleep
    print ("==============bought:%d sold:%d"%(bought_num,sold_num))
    print "finished this round. Sleeping........."
    time.sleep(5)
    
bought_num=0
sold_num =0        
while True:
    do_main()

# if __name__ == "__main__":
    # do_main()
