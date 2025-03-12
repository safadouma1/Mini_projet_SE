import threading
import time
import random

# Ressources partagées : stations de recharge
stations_de_recharge = [1, 2]  # Deux stations disponibles

# Verrous pour simuler l'interblocage
lock1 = threading.Lock()  #Deux stations disponibles
lock2 = threading.Lock()  

# Sémaphore pour éviter l'interblocage
semaphore = threading.Semaphore(1)  # Un seul thread peut acquérir les verrous à la fois

class Drone(threading.Thread):
    def __init__(self, drone_id, battery=100):
        threading.Thread.__init__(self)
           #Lorsque on hérite de classe Thread,on appel toujours threading.Thread.__init__(self) dans le constructeur de votre classe pour initialiser le thread.
          #doit être appelée avant d'ajouter des initialisations spécifiques de la classe Drone
        self.drone_id = drone_id  # Identifiant du drone
        self.battery = battery  # Niveau de batterie du drone
        self.is_delivering = False  # Indicateur de livraison en cours

    def run(self):
        """
        Méthode principale exécutée par chaque thread de drone.
        Le drone effectue des livraisons et se recharge jusqu'à ce que sa batterie soit épuisée.
        """
        while self.battery > 0:
            self.deliver()  # Effectuer une livraison
            self.recharge()  # Se recharger
        print(f"Drone {self.drone_id} : Batterie épuisée, arrêt.")

    def deliver(self):
        """
        Simule une livraison en mettant le drone en pause pendant un temps aléatoire
        et en réduisant sa batterie.
        """
        self.is_delivering = True
        print(f"Drone {self.drone_id} : Livraison en cours...")
        time.sleep(random.randint(1, 2))  # Temps de livraison aléatoire
        self.battery -= random.randint(10, 20)  # Réduire la batterie
        print(f"Drone {self.drone_id} : Livraison terminée. Batterie restante : {self.battery}%")
        self.is_delivering = False

    def recharge(self):
        """
        Gère la recharge du drone en utilisant les stations de recharge partagées.
        Utilise un sémaphore pour éviter les interblocages.
        Si un interblocage est détecté, un message est affiché.
        """
        # Acquérir le sémaphore pour éviter l'interblocage
        semaphore.acquire()

        # Acquisition des verrous avec timeout pour détecter l'interblocage
        if self.drone_id % 2 == 1:  # Drone impair (1, 3, ...)
            print(f"Drone {self.drone_id} : Tentative d'acquisition de lock1...")
            if not lock1.acquire(timeout=1):  # Réduire le timeout
                print(f"Interblocage détecté. Drone {self.drone_id} ne peut pas acquérir lock1.")
                semaphore.release()  # Libérer le sémaphore avant de quitter
                return  # Quitter la méthode si le verrou n'est pas acquis
            print(f"Drone {self.drone_id} : lock1 acquis.")
            time.sleep(1)  # Délai pour augmenter les chances d'interblocage
            print(f"Drone {self.drone_id} : Tentative d'acquisition de lock2...")
            if not lock2.acquire(timeout=1):  # Réduire le timeout
                print(f"Interblocage détecté. Drone {self.drone_id} ne peut pas acquérir lock2.")
                lock1.release()  # Libérer lock1 avant de quitter
                semaphore.release()  # Libérer le sémaphore avant de quitter
                return  # Quitter la méthode si le verrou n'est pas acquis
            print(f"Drone {self.drone_id} : lock2 acquis.")
        else:  # Drone pair (2, 4, ...)
            print(f"Drone {self.drone_id} : Tentative d'acquisition de lock2...")
            if not lock2.acquire(timeout=1):  # Réduire le timeout
                print(f"Interblocage détecté. Drone {self.drone_id} ne peut pas acquérir lock2.")
                semaphore.release()  # Libérer le sémaphore avant de quitter
                return  # Quitter la méthode si le verrou n'est pas acquis
            print(f"Drone {self.drone_id} : lock2 acquis.")
            time.sleep(1)  # Délai pour augmenter les chances d'interblocage
            print(f"Drone {self.drone_id} : Tentative d'acquisition de lock1...")
            if not lock1.acquire(timeout=1):  # Réduire le timeout
                print(f"Interblocage détecté. Drone {self.drone_id} ne peut pas acquérir lock1.")
                lock2.release()  # Libérer lock2 avant de quitter
                semaphore.release()  # Libérer le sémaphore avant de quitter
                return  # Quitter la méthode si le verrou n'est pas acquis
            print(f"Drone {self.drone_id} : lock1 acquis.")

        # Simulation de la recharge
        if stations_de_recharge:
            station = stations_de_recharge.pop(0)  # Utiliser une station disponible(pop from liste pour que aucun autre drone accéde a la meme station)
            print(f"Drone {self.drone_id} : Recharge à la station {station}.")
            time.sleep(random.randint(1, 2))  # Temps de recharge aléatoire
            self.battery = 100  # Recharger la batterie à 100 %
            stations_de_recharge.append(station)  # Remettre la station dans la liste
            print(f"Drone {self.drone_id} : Recharge terminée. Batterie : 100%")
        else:
            print(f"Drone {self.drone_id} : Aucune station disponible, attente...")
            time.sleep(1)  # Attendre avant de réessayer

        # Libération des verrous
        if self.drone_id % 2 == 1:  # Drone impair (1, 3, ...)
            lock2.release()
            print(f"Drone {self.drone_id} : lock2 libéré.")
            lock1.release()
            print(f"Drone {self.drone_id} : lock1 libéré.")
        else:  # Drone pair (2, 4, ...)
            lock1.release()
            print(f"Drone {self.drone_id} : lock1 libéré.")
            lock2.release()
            print(f"Drone {self.drone_id} : lock2 libéré.")

        # Libérer le sémaphore après avoir libéré les verrous
        semaphore.release()

# Création des drones
drones = [Drone(i) for i in range(1, 5)]  # Créer 4 drones

# Démarrage des drones
for drone in drones:
    drone.start()

# Attendre que les drones terminent
for drone in drones:
    drone.join()

print("Simulation terminée.")
