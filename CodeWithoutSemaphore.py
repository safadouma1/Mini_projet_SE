import threading
import time
import random
import sys

# Ressources partagées : stations de recharge
stations_de_recharge = [1, 2]  # Deux stations disponibles

# Verrous pour simuler l'interblocage
lock1 = threading.Lock()  
lock2 = threading.Lock()  #  Deux stations disponibles

# Variable globale pour détecter l'interblocage
interblocage_detecte = False

class Drone(threading.Thread):
    def __init__(self, drone_id, battery=100):
        threading.Thread.__init__(self)
        self.drone_id = drone_id
        self.battery = battery
        self.is_delivering = False

    def run(self):
        while self.battery > 0 and not interblocage_detecte:
            self.deliver()
            self.recharge()
        if interblocage_detecte:
            print(f"Drone {self.drone_id} : Arrêt d'urgence en raison d'un interblocage.")
        else:
            print(f"Drone {self.drone_id} : Batterie épuisée, arrêt.")

    def deliver(self):
        self.is_delivering = True
        time.sleep(random.randint(1, 2))  # Simuler le temps de livraison
        self.battery -= random.randint(10, 20)
        self.is_delivering = False

    def recharge(self):
        global interblocage_detecte

        # Vérifier si un interblocage a déjà été détecté
        if interblocage_detecte:
            return

        # Acquisition des verrous avec timeout pour détecter l'interblocage
        if self.drone_id % 2 == 1:  # Drone impair (1, 3, ...)
            print(f"Drone {self.drone_id} : Tentative d'acquisition de lock1...")
            if not lock1.acquire(timeout=1):  # Réduire le timeout
                print(f"Interblocage détecté. Drone {self.drone_id} ne peut pas acquérir lock1.")
                interblocage_detecte = True  # Signalement de l'interblocage
                return  # Quitter la méthode si le verrou n'est pas acquis
            print(f"Drone {self.drone_id} : lock1 acquis.")
            time.sleep(1)  # Délai pour augmenter les chances d'interblocage
            print(f"Drone {self.drone_id} : Tentative d'acquisition de lock2...")
            if not lock2.acquire(timeout=1):  # Réduire le timeout
                print(f"Interblocage détecté. Drone {self.drone_id} ne peut pas acquérir lock2.")
                lock1.release()  # Libérer lock1 avant de quitter
                interblocage_detecte = True  # Signalement de l'interblocage
                return  # Quitter la méthode si le verrou n'est pas acquis
            print(f"Drone {self.drone_id} : lock2 acquis.")
        else:  # Drone pair (2, 4, ...)
            print(f"Drone {self.drone_id} : Tentative d'acquisition de lock2...")
            if not lock2.acquire(timeout=1):  # Réduire le timeout
                print(f"Interblocage détecté. Drone {self.drone_id} ne peut pas acquérir lock2.")
                interblocage_detecte = True  # Signalement de l'interblocage
                return  # Quitter la méthode si le verrou n'est pas acquis
            print(f"Drone {self.drone_id} : lock2 acquis.")
            time.sleep(1)  # Délai pour augmenter les chances d'interblocage
            print(f"Drone {self.drone_id} : Tentative d'acquisition de lock1...")
            if not lock1.acquire(timeout=1):  # Réduire le timeout
                print(f"Interblocage détecté. Drone {self.drone_id} ne peut pas acquérir lock1.")
                lock2.release()  # Libérer lock2 avant de quitter
                interblocage_detecte = True  # Signalement de l'interblocage
                return  # Quitter la méthode si le verrou n'est pas acquis
            print(f"Drone {self.drone_id} : lock1 acquis.")

        # Simulation de la recharge
        if stations_de_recharge:
            station = stations_de_recharge.pop(0)
            print(f"Drone {self.drone_id} : Recharge à la station {station}.")
            time.sleep(random.randint(1, 2))  # Réduire le temps de recharge
            self.battery = 100
            stations_de_recharge.append(station)
            print(f"Drone {self.drone_id} : Recharge terminée. Batterie : 100%")
        else:
            print(f"Drone {self.drone_id} : Aucune station disponible, attente...")
            time.sleep(1)  # Réduire le temps d'attente

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

# Création des drones
drones = [Drone(i) for i in range(1, 5)]  # Créer 4 drones

# Démarrage des drones
for drone in drones:
    drone.start()

# Attendre que les drones terminent
for drone in drones:
    drone.join()

print("Simulation terminée.")
