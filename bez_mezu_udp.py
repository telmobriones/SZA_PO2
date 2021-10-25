import socket, sys

SERVER = 'localhost'
PORT = 50006
MAX_BUF = 1024
MAX_MEZU = 140

ER_MSG = (
"Dena ondo. Errorerik ez.",
"Komando ezezaguna edo ustegabekoa.",
"Espero ez zen parametroa. Parametro bat jaso da espero ez zen tokian.",
"Hautazkoa ez den parametro bat falta da.",
"Parametroak ez du formatu egokia.",
"Segurtasun kode okerra." ,
"Erabiltzailea erabileran dago.",
"Posta elektronikoa beste erabiltzaile bati dagokio.",
"Ezin izan da identifikatu.",
"Jasotzailea ez dago sisteman",
"Mezua luzeegia da."  )

class Command:
    Register, Identify, Message, Read, Exit = ("RG", "ID", "MS", "RD", "XT")

# Erregistratzeko eta saioa hasteko menua
class Menua:
    Register, Identify, Exit = range( 1, 4 )
    Options = ( "Erregistratu", "Identifikatu", "Itxi" )

    def menua():
        print( "+{}+".format( '-' * 30 ) )
        for i,option in enumerate( Menua.Options, 1 ):
                print( "| {}.- {:<25}|".format( i, option ) )
                print( "+{}+".format( '-' * 30 ) )
    
        while True:
            try:
                selected = int( input( "Egin zure aukera: " ) )
            except:
                print( "Aukera okerra, saiatu berriro." )
                continue
            if 0 < selected <= len( Menua.Options ):
                return selected
            else:
                print( "Aukera okerra, saiatu berriro." )


# Behin saioa hasita erakusten den menua
class MenuaBi:
    Message, Read, Exit = range( 1, 4 )
    OptionsBi = ( "Mezua bidali"," Mezua irakurri", "Irten" )

    def menuaBi():
        print( "+{}+".format( '-' * 30 ) )
        for i,optionBi in enumerate( MenuaBi.OptionsBi, 1 ):
            print( "| {}.- {:<25}|".format( i, optionBi ) )
            print( "+{}+".format( '-' * 30 ) )
            
        while True:
            try:
                selectedBi = int( input( "Egin zure aukera: " ) )
            except:
                print( "Aukera okerra, saiatu berriro." )
                continue
            if 0 < selectedBi <= len( MenuaBi.OptionsBi ):
                return selectedBi
            else:
                print( "Aukera okerra, saiatu berriro." )


# Erroreak dauden identifikatzeko eta pantailaratzeko funtzioa
def iserror( message ):
    if( message.startswith( "ER" ) ):
        code = int( message[2:] )
        print( ER_MSG[code] )
        return True
    else:
        return False


if __name__ == "__main__":
    if len( sys.argv ) != 2:
	    print( "Erabilera: {} <Zerbitzari izena | IPv4 helbidea>".format( sys.argv[0] ) )
	    exit( 1 )

    zerb_helb = (sys.argv[1], PORT)
    entzuten = False

    # Socketa sortzen dugu
    s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

    # Saiorako kodea gordetzeko
    kodea = None
    while True:
        option = Menua.menua()

        # ERREGISTRATU
        if option == Menua.Register:
            user = input( "Erabiltzaile izena: " ) + "#"
            password = input( "Pasahitza sortu: " ) + "#"
            email = input( "Posta elektroniko helbidea: " )
            rMezua = "{}{}{}{}{}".format( Command.Register," ", user, password, email )

            # Zerbitzariaren entzute socketari EZ bagaude konektatuta
            if not entzuten:
                s.sendto( rMezua.encode("ascii"), zerb_helb )
                buf, zerb_helb2 = s.recvfrom( MAX_BUF )
                
                s.connect( zerb_helb2 )
                entzuten = True

                eranR = buf.decode()
            
            # Zerbitzariaren entzute socketari konektatuta bagaude
            else:
                s.send(rMezua.encode( "ascii" ))
                eranR = s.recv( MAX_BUF ).decode( "ascii" )
            
            if iserror( eranR ):
                continue
        
        # ITXI
        elif option == Menua.Exit:
            s.close()
            break
        
        # IDENTIFIKATU
        elif option == Menua.Identify:
            user = input( "Erabiltzaile izena: " ) + "#"
            password = input( "Pasahitza: " )
            iMezua = "{}{}{}{}".format( Command.Identify," ", user, password )
            
            # Zerbitzariaren entzute socketari EZ bagaude konektatuta
            if not entzuten:
                s.sendto( iMezua.encode("ascii"), zerb_helb )
                buf, zerb_helb2 = s.recvfrom( MAX_BUF )

                s.connect( zerb_helb2 )
                entzuten = True

                eranI = buf.decode()
            
            # Zerbitzariaren entzute socketari konektatuta bagaude
            else:
                s.send(iMezua.encode( "ascii" ))
                eranI = s.recv( MAX_BUF ).decode( "ascii" )
            

            # Erantzuna positiboa bada, kodea lortu eta jarraitu
            if not iserror(eranI):
                kodea = eranI.split(" ",1)[1]
            else:
                s.close()
                break
            

            while True:              
                optionBi = MenuaBi.menuaBi()
                
                # MEZUAK BIDALI
                if optionBi == MenuaBi.Message:
                    jasotzaile = input("Idaztzi jasotzailearen erabiltzailea: ") + "#"
                    mMezua = input("Idatzi bidali nahi duzun mezua: ")
                    kode = kodea + "#"
                    sMezua = "{}{}{}{}".format( Command.Message," ", kode, jasotzaile )
                    s.send(sMezua.encode("ascii") + mMezua.encode("utf8"))
                    eranM = s.recv( MAX_BUF ).decode("ascii")
                    
                    if not iserror(eranM):
                        print("Mezua zuzenki bidali da.")
                
                # MEZUAK IRAKURRI
                elif optionBi == MenuaBi.Message:
                    rdMezua = "{}{}{}".format( Command.Read," ", kodea )
                    s.send(rdMezua.encode("ascii"))
                    eranRd = s.recv( MAX_BUF ).decode("ascii")

                    if not iserror(eranRd):
                        if eranRd.split(" ",1)[1] == 0:
                           print("Ez dago mezu berririk irakurtzeko.") 

                        else:
                            print(eranRd.split(" ",1)[1] + " mezu dituzu irakurtzeko: ")
                            n = eranRd.split(" ",1)[1]
                            while n != 0:
                                mezu_Pakete = s.recv( MAX_BUF ).decode("ascii")
                                bidaltzailea = mezu_Pakete.split("#",1)[0]
                                mezua = mezu_Pakete.split("#",1)[1]
                                print("\n\nBidaltzailea: " + bidaltzailea + "\nMezua: " + mezua)
                                print(".·"*14)
                                n -= 1 
                            print("Ez da mezurik geratzen!\n\n")

                # ITXI            
                elif optionBi == MenuaBi.Exit:
                    eMezua = "{}{}{}".format( Command.Exit," ", kodea )
                    s.send( eMezua.encode( "ascii" ) )
                    s.close()
                    break