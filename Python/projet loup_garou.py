import tkinter as tk
from tkinter import simpledialog, messagebox
import random
from PIL import Image, ImageTk

root = tk.Tk()
root.title("Loup Garou")
root.geometry("400x200")

players = []
roles = []
mechant = ["loup garou"]
bien = ["villageois simple", "voyante", "enfant sauvage", "sorciere", "chasseur"]
dic = {}
loup = []
vellageois = []
pouvoir_sorciere = []
capitaine = None
current_player_idx = 0
N = 0
enfant_sauvage_model = None
enfant_sauvage_player = None

role_images = {
    "loup garou": "loup.jpg",
    "sorciere": "sahara.png",
    "voyante": "chwafa.jpg",
    "villageois simple": "simple-villageois.png",
    "enfant sauvage": "savage.jpg",
    "chasseur": "chaseure.jpg"  # Add this line
}

def ask_num_players():
    global N, roles
    N = simpledialog.askinteger("Nombre de joueurs", "Entrez le nombre de joueurs (4-12):", minvalue=4, maxvalue=12)
    if N is None:
        root.destroy()
        return
    # Calculate number of loups
    nb_villageois = N
    nb_loups = max(1, (nb_villageois // 2) - 1)
    nb_villageois -= nb_loups
    # Always include 1 voyante, 1 sorciere, 1 enfant sauvage if possible
    special_roles = []
    if nb_villageois >= 4:
        special_roles = ["voyante", "sorciere", "enfant sauvage", "chasseur"]
        nb_villageois -= 4
    elif nb_villageois == 3:
        special_roles = ["voyante", "sorciere", "enfant sauvage"]
        nb_villageois -= 33
    elif nb_villageois == 2:
        special_roles = ["voyante", "sorciere"]
        nb_villageois -= 2
    elif nb_villageois == 1:
        special_roles = ["voyante"]
        nb_villageois -= 1
    roles = ["loup garou"] * nb_loups + special_roles + ["villageois simple"] * nb_villageois
    random.shuffle(roles)
    root.after(100, ask_player_name)

def ask_player_name():
    global current_player_idx
    if current_player_idx < N:
        name = simpledialog.askstring("Nom du joueur", f"Joueur {current_player_idx+1}, entrez votre nom :")
        if not name or name in players:
            messagebox.showerror("Erreur", "Nom invalide ou déjà utilisé.")
            root.after(100, ask_player_name)
            return
        players.append(name)
        root.after(100, assign_role_to_player)
    else:
        root.after(100, start_game)

def show_role_with_image(player, role):
    img_path = role_images.get(role)
    if img_path:
        img = Image.open(img_path)
        img = img.resize((200, 200))
        photo = ImageTk.PhotoImage(img)
        top = tk.Toplevel(root)
        top.title("Votre rôle")
        label = tk.Label(top, text=f"{player}, votre rôle est : {role}", font=("Arial", 14))
        label.pack(pady=10)
        img_label = tk.Label(top, image=photo)
        img_label.image = photo  # keep a reference!
        img_label.pack()
        btn = tk.Button(top, text="OK", command=top.destroy)
        btn.pack(pady=10)
        top.grab_set()
        root.wait_window(top)
    else:
        messagebox.showinfo("Votre rôle", f"{player}, votre rôle est : {role}")

def assign_role_to_player():
    global current_player_idx, dic, roles, pouvoir_sorciere, enfant_sauvage_player
    if not roles:
        messagebox.showerror("Erreur", "Plus de rôles disponibles.")
        root.destroy()
        return
    role = roles.pop()
    dic[players[current_player_idx]] = role
    if role == "sorciere":
        pouvoir_sorciere.clear()
        pouvoir_sorciere.extend(["poison", "revivre"])
    if role == "enfant sauvage":
        enfant_sauvage_player = players[current_player_idx]
    show_role_with_image(players[current_player_idx], role)
    current_player_idx += 1
    root.after(100, ask_player_name)

def start_game():
    global loup, vellageois, capitaine
    loup.clear()
    vellageois.clear()
    for player in dic:
        if dic[player] == "loup garou":
            loup.append(player)
        else:
            vellageois.append(player)
    capitaine = random.choice(players)
    messagebox.showinfo("Capitaine", f"Le capitaine est : {capitaine}")
    update_status()
    root.after(100, enfant_sauvage_phase)

def update_status():
    status = f"Joueurs restants: {', '.join(players)}"
    status_label.config(text=status)

def enfant_sauvage_phase():
    global enfant_sauvage_model
    if enfant_sauvage_player:
        model = simpledialog.askstring(
            "Enfant Sauvage",
            f"{enfant_sauvage_player}, choisis un joueur à admirer (si ce joueur meurt, tu deviens loup garou):\nJoueurs: {', '.join([p for p in players if p != enfant_sauvage_player])}"
        )
        while model not in players or model == enfant_sauvage_player:
            model = simpledialog.askstring(
                "Enfant Sauvage",
                f"Nom invalide. {enfant_sauvage_player}, choisis un joueur à admirer :\nJoueurs: {', '.join([p for p in players if p != enfant_sauvage_player])}"
            )
        enfant_sauvage_model = model
    root.after(100, loups_phase)
#mo
def loups_phase():
    if not loup or len(players) <= 1:
        root.after(100, sorciere_phase)
        return
    # Loups vote ensemble (one vote for the group)
    possible_targets = [p for p in players if p not in loup]
    if not possible_targets:
        root.after(100, sorciere_phase)
        return
    votee = simpledialog.askstring(
        "Loups",
        f"Loups garous, qui voulez-vous éliminer ?\nCibles: {', '.join(possible_targets)}"
    )
    while votee not in possible_targets:
        votee = simpledialog.askstring(
            "Loups",
            f"Nom invalide. Loups garous, qui voulez-vous éliminer ?\nCibles: {', '.join(possible_targets)}"
        )
    victim = votee
    root.after(100, lambda: sorciere_phase(victim))

def sorciere_phase(victim=None):
    global pouvoir_sorciere
    saved = False
    killed_by_sorciere = None
    
    # Sorcière peut sauver la victime
    if "sorciere" in dic.values() and pouvoir_sorciere:
        sorciere_player = [p for p in dic if dic[p] == "sorciere" and p in players]
        if sorciere_player:
            sorciere_player = sorciere_player[0]
            if "revivre" in pouvoir_sorciere and victim:
                reponse = simpledialog.askstring(
                    "Sorcière",
                    f"{sorciere_player}, veux-tu sauver {victim} ? (oui/non)"
                )
                if reponse and reponse.lower().startswith("o"):
                    pouvoir_sorciere.remove("revivre")
                    saved = True
            # Sorcière peut tuer quelqu'un
            if "poison" in pouvoir_sorciere:
                cible = simpledialog.askstring(
                    "Sorcière",
                    f"{sorciere_player}, veux-tu éliminer un joueur ? (laisse vide pour passer)\nJoueurs: {', '.join([p for p in players if p != sorciere_player])}"
                )
                if cible and cible in players and cible != sorciere_player:
                    pouvoir_sorciere.remove("poison")
                    killed_by_sorciere = cible
    # Appliquer les effets
    if victim and not saved:
        eliminate_player(victim)
    if killed_by_sorciere:
        eliminate_player(killed_by_sorciere)
    root.after(100, voyante_phase)
    

def voyante_phase():
    voyante_player = [p for p in dic if dic[p] == "voyante" and p in players]
    if voyante_player:
        voyante_player = voyante_player[0]
        cible = simpledialog.askstring(
            "Voyante",
            f"{voyante_player}, choisis un joueur à révéler :\nJoueurs: {', '.join([p for p in players if p != voyante_player])}"
        )
        while cible not in players or cible == voyante_player:
            cible = simpledialog.askstring(
                "Voyante",
                f"Nom invalide. {voyante_player}, choisis un joueur à révéler :\nJoueurs: {', '.join([p for p in players if p != voyante_player])}"
            )
        role = dic.get(cible, "inconnu")
        show_role_with_image(cible, role)
    root.after(100, vote_phase)

def eliminate_player(player):
    global enfant_sauvage_model, enfant_sauvage_player, capitaine
    if player not in players:
        return

    # Capitaine succession BEFORE elimination (by any means)
    if player == capitaine and len(players) > 1:
        possible_successors = [p for p in players if p != capitaine]
        if possible_successors:
            new_cap = simpledialog.askstring(
                "Nouveau capitaine",
                f"{capitaine}, vous êtes éliminé. Désignez votre successeur parmi : {', '.join(possible_successors)}"
            )
            while new_cap not in possible_successors:
                new_cap = simpledialog.askstring(
                    "Nouveau capitaine",
                    f"Nom invalide. {capitaine}, désignez votre successeur parmi : {', '.join(possible_successors)}"
                )
            capitaine = new_cap
            messagebox.showinfo("Capitaine", f"Le nouveau capitaine est : {capitaine}")
        else:
            capitaine = None

    # Chasseur effect: eliminate another player if chasseur is eliminated
    if dic.get(player) == "chasseur" and len(players) > 1:
        possible_targets = [p for p in players if p != player]
        cible = simpledialog.askstring(
            "Chasseur",
            f"{player} (chasseur), vous êtes éliminé ! Choisissez un joueur à éliminer avec vous :\nJoueurs: {', '.join(possible_targets)}"
        )
        while cible not in possible_targets:
            cible = simpledialog.askstring(
        
                "Chasseur",
                f"Nom invalide. {player}, choisissez un joueur à éliminer avec vous :\nJoueurs: {', '.join(possible_targets)}"
            )
        show_role_with_image(player, dic.get(player, "inconnu"))
        # Remove chasseur first, then eliminate the target
        players.remove(player)
        role = dic.pop(player)
        if player in loup:
            loup.remove(player)
        if player in vellageois:
            vellageois.remove(player)
        # Enfant sauvage devient loup si son modèle est mort
        if enfant_sauvage_player and enfant_sauvage_model == player and enfant_sauvage_player in players:
            dic[enfant_sauvage_player] = "loup garou"
            loup.append(enfant_sauvage_player)
            if enfant_sauvage_player in vellageois:
                vellageois.remove(enfant_sauvage_player)
            messagebox.showinfo("Transformation", f"{enfant_sauvage_player} devient loup garou !")
        update_status()
        eliminate_player(cible)
        return

    # Normal elimination
    show_role_with_image(player, dic.get(player, "inconnu"))
    players.remove(player)
    role = dic.pop(player)
    if player in loup:
        loup.remove(player)
    if player in vellageois:
        vellageois.remove(player)
    # Enfant sauvage devient loup si son modèle est mort
    if enfant_sauvage_player and enfant_sauvage_model == player and enfant_sauvage_player in players:
        dic[enfant_sauvage_player] = "loup garou"
        loup.append(enfant_sauvage_player)
        if enfant_sauvage_player in vellageois:
            vellageois.remove(enfant_sauvage_player)
        messagebox.showinfo("Transformation", f"{enfant_sauvage_player} devient loup garou !")
    update_status()
#om
def vote_phase():
    global capitaine
    if len(players) <= 1:
        
        messagebox.showinfo("Fin", "Plus assez de joueurs pour voter.")
        return
    votes = {}
    for voter in players:
        possible_targets = [p for p in players if p != voter]
        if not possible_targets:
            continue
        votee = simpledialog.askstring(
            "Vote",
            f"{voter}, qui voulez-vous éliminer ?\nJoueurs: {', '.join(possible_targets)}"
        )
        while votee not in possible_targets:
            votee = simpledialog.askstring(
                "Vote",
                f"{voter}, nom invalide. Qui voulez-vous éliminer ?\nJoueurs: {', '.join(possible_targets)}"
            )
        # Capitaine's vote counts as 2
        vote_value = 2 if voter == capitaine else 1
        votes[votee] = votes.get(votee, 0) + vote_value
    max_votes = max(votes.values())
    eliminated = [p for p, v in votes.items() if v == max_votes]
    eliminated_player = random.choice(eliminated)

    eliminate_player(eliminated_player)
    update_status()
    if not check_end_game():
        # Start a new round if the game is not finished
        root.after(100, loups_phase)

def check_end_game():
    if len(loup) == 0:
        messagebox.showinfo("Fin", "Les villageois ont gagné !")
        root.destroy()
        return True
    elif len(loup) >= len(vellageois):
        messagebox.showinfo("Fin", "Les loups ont gagné !")
        root.destroy()
        return True
    return False

status_label = tk.Label(root, text="", font=("Arial", 12))
status_label.pack(pady=10)

vote_btn = tk.Button(root, text="Voter pour éliminer", command=vote_phase, font=("Arial", 12))

ask_num_players()
root.mainloop()
