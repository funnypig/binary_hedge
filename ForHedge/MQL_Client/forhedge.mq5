//+------------------------------------------------------------------+

//|                                                     forhedge.mq5 |

//|                                          ilya.antipiev@gmail.com |

//|                                             https://www.mql5.com |

//+------------------------------------------------------------------+

#property copyright "ilya.antipiev@gmail.com"

#property link      "https://www.mql5.com"

#property version   "1.00"

//--- input parameters

input int      PORT=64999;

input string   HOST="127.0.0.1";

//+------------------------------------------------------------------+

//| Expert initialization function                                   |

//+------------------------------------------------------------------+

int OnInit()

  {

//---



//---

   return(INIT_SUCCEEDED);

  }

//+------------------------------------------------------------------+

//| Expert deinitialization function                                 |

//+------------------------------------------------------------------+

void OnDeinit(const int reason)

  {

//---



  }

//+------------------------------------------------------------------+

//| Expert tick function                                             |

//+------------------------------------------------------------------+

void OnTick()

  {

//---



  }

//+------------------------------------------------------------------+

//| Sends message to server                                          |

//+------------------------------------------------------------------+

bool socksend(int sock,string request)

  {

   char req[];

   int  len=StringToCharArray(request,req)-1;

   if(len<0)

      return(false);

   return(SocketSend(sock,req,len)==len);

  }

//+------------------------------------------------------------------+

//| Receives message from server                                     |

//+------------------------------------------------------------------+

string socketreceive(int sock,int timeout)

  {

   char rsp[];

   string result="";

   uint len;

   uint timeout_check=GetTickCount()+timeout;

   do

     {

      len=SocketIsReadable(sock);

      if(len)

        {

         int rsp_len;

         rsp_len=SocketRead(sock,rsp,len,timeout);

        }

     }

   while((GetTickCount()<timeout_check) && !IsStopped());

   return result;

  }

//+------------------------------------------------------------------+

//| TradeTransaction function. Sends transaction info to server      |

//+------------------------------------------------------------------+

void OnTradeTransaction(const MqlTradeTransaction &transaction,

                        const MqlTradeRequest &request,

                        const MqlTradeResult &result)

  {

//---

   static uint last_trade_time=0;



   uint cur_time=GetTickCount();



   if(cur_time-last_trade_time<1000)

     {

      // the trade is already processed

      return;

     }





   if(transaction.type==TRADE_TRANSACTION_DEAL_ADD)

     {



      last_trade_time=cur_time;

      int socket= SocketCreate();

      if(socket!=INVALID_HANDLE)

        {

         if(SocketConnect(socket,HOST,PORT,1000))

           {

            string toSend=TransactionDescription(transaction);

            string received=socksend(socket,toSend) ? socketreceive(socket,1000) : "";

           }

         SocketClose(socket);

        }

     }

  }

//+------------------------------------------------------------------+

//+------------------------------------------------------------------+

//| Returns text representation of transaction                       |

//+------------------------------------------------------------------+

string TransactionDescription(const MqlTradeTransaction &trans)

  {

//---

   string desc=EnumToString(trans.type)+"\r\n";

   desc+="Symbol: "+trans.symbol+"\r\n";

   desc+="Deal ticket: "+(string)trans.deal+"\r\n";

   desc+="Deal type: "+EnumToString(trans.deal_type)+"\r\n";

   desc+="Order ticket: "+(string)trans.order+"\r\n";

   desc+="Order type: "+EnumToString(trans.order_type)+"\r\n";

   desc+="Order state: "+EnumToString(trans.order_state)+"\r\n";

   desc+="Order time type: "+EnumToString(trans.time_type)+"\r\n";

   desc+="Order expiration: "+TimeToString(trans.time_expiration)+"\r\n";

   desc+="Price: "+StringFormat("%G",trans.price)+"\r\n";

   desc+="Price trigger: "+StringFormat("%G",trans.price_trigger)+"\r\n";

   desc+="Stop Loss: "+StringFormat("%G",trans.price_sl)+"\r\n";

   desc+="Take Profit: "+StringFormat("%G",trans.price_tp)+"\r\n";

   desc+="Volume: "+StringFormat("%G",trans.volume)+"\r\n";

   desc+="Position: "+(string)trans.position+"\r\n";

   desc+="Position by: "+(string)trans.position_by+"\r\n";

//--- return built string

   return desc;

  }

//+------------------------------------------------------------------+