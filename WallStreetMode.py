#Ici c'est le coeur du truc, qui va tourner en fond et gérer la soirée

isRunning = True

def CalculPrix(): #Renvoie [(id1,prix1),(id2,prix2) ...]
    Conso_total_periode = SQL_SELECT(QUERRY_getConsoTotalePeriode())[0][0]
    Conso_total_avant = SQL_SELECT(QUERRY_getConsoTotalePeriodeMoinsUn())[0][0]
    Produits_periode = SQL_SELECT(QUERRY_getIdPrixProduits())
    Produits_periode_futur = []


    #Calul de A
    Lcpp , Lcpa = [],[] #listes consos produits periode et periode avant
    CA_total_Kfet = 0
    for i in range(len(Produits_periode)):
        produit = Produits_periode[i]
        Conso_produit_periode = SQL_SELECT(QUERRY_getConsoPeriode(produit[0]))[0][0]
        Conso_produit_avant = SQL_SELECT(QUERRY_getConsoPeriodeMoinsUn(produit[0]))[0][0]
        Lcpp.append(Conso_produit_periode) #permet de pas refaire sql
        Lcpa.append(Conso_produit_avant)
        CA_total_Kfet += Lcpp[i]*produits_standard[i][1]

    if Conso_total_periode == 0:
        print("Pas de consos sur la période")
        return Produits_periode, Lcpp

    CA_total_P3 = 0
    for i in range(len(Produits_periode)):
        CA_total_P3 += Lcpp[i]*Produits_periode[i][1]

    A = CA_total_Kfet - CA_total_P3
    for i in range(len(Produits_periode)):
        #Calcul des nouveaux prix
        if Lcpp[i] == 0:
            x = 0
        else :
            x = A / Lcpp[i]
        if Lcpp[i] > Lcpa[i]:
            #print(int(produits_standard[i][1]*(1+(Lcpp[i]/Conso_total_periode))*100)/100)
            # print(Conso_produit_periode)
            # print(Conso_total_periode)
            Produits_periode_futur.append((produits_standard[i][0] , max(int(100*produits_standard[i][1]/2)/100,int((produits_standard[i][1] + (Lcpp[i] / Conso_total_periode) * coef_lingus) * 100) / 100)))
        else :
            Produits_periode_futur.append((produits_standard[i][0] , max(int(100*produits_standard[i][1]/2)/100, int((produits_standard[i][1] - (1 - Lcpp[i] / Conso_total_periode) * coef_lingus) * 100) / 100)))
    print('consos anciens : ', Lcpa)
    print('conso période :', Lcpp)
    print('prix période : ', Produits_periode)
    print('prix nouveaux : ',Produits_periode_futur)
    return Produits_periode_futur, Lcpp

periodes_jouees = 0
while True:
    if periodes_jouees >= Nb_de_Periodes:
        isRunning = False
    periodes_jouees += 1

    print(datetime.now().strftime("%H:%M:%S"))

    if isRunning != previous_state: #permet de constater que le jeu démarre ou s'arrête

        if isRunning: # si c'est un demarrage, on stock les bons prix
            produits_standard = SQL_SELECT(QUERRY_getIdPrixProduits())
            #print(produits_standard)
            for produit in produits_standard:
                name_produit.append(produit[2])
            with open("name_produit.txt",'wb') as fp:
                pickle.dump(name_produit,fp)
            print("\nLes produits joués sont: ",name_produit,"\n")
        previous_state = isRunning

    if isRunning: #On a deja demarré et on est en jeu

    ### 1ème étape: Calcul des nouveaux prix à partir des formules de Lingus.
        prix_p3_futur, Lcpp_temp = CalculPrix()
        all_Lccp.append(Lcpp_temp)
        all_prix.append([item[1] for item in prix_p3_futur])
        with open("all_lccp.txt",'wb') as fp:
            pickle.dump(all_Lccp,fp)
        with open("all_prix.txt",'wb') as fp:
            pickle.dump(all_prix,fp)
        with open("all_lccp.txt", "rb") as fp:
            test = pickle.load(fp)
        #print(all_Lccp,all_prix)
        #print("test:",test)

	### 2ème étape: UPDATE des prix kfet dans la bdd
        querrys = ""
        for produit in prix_p3_futur :
            querrys += QUERRY_setMontant(produit[0], produit[1])
        SQL_UPDATE(querrys)

    else: # On a arrété le jeu et tout est remis en place, on quitte
        querrys = ""
        for produit in produits_standard:
            querrys += QUERRY_setMontant(produit[0],produit[1])
        SQL_UPDATE(querrys)
        print("\nremise à zero prix")
        previous_state = isRunning
        break
    print("\nIl reste'{0}' manches de '{1}' min.\n".format(1+Nb_de_Periodes - periodes_jouees,time_period))
    time.sleep(time_period_second)
