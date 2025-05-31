import random
import customtkinter as ctk
from tkinter import messagebox
import time

class Particule:
    def __init__(self, n):
        self.n = n
        self.position = random.sample(range(n), n)
        self.vitesse = [random.uniform(-1, 1) for _ in range(n)]
        self.pBest = self.position.copy()
        self.score_pBest = self.fitness()

    def fitness(self):
        return compter_conflits_total(self.position)

def compter_conflits_total(solution):
    """Calcule le nombre de conflits entre les reines placées sur l'échiquier."""
    conflits = 0
    n = len(solution)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(solution[i] - solution[j]) == abs(i - j):
                conflits += 1
    return conflits

def mise_a_jour_vitesse_et_position(particule, gBest, w=0.7, c1=2.0, c2=2.0):
    """Met à jour la vitesse et la position d'une particule en tenant compte de son historique et du meilleur global."""
    n = particule.n
    for i in range(n):
        r1, r2 = random.random(), random.random()
        particule.vitesse[i] = (w * particule.vitesse[i] +
                                c1 * r1 * (particule.pBest[i] - particule.position[i]) +
                                c2 * r2 * (gBest[i] - particule.position[i]))

    # Normalisation de la position
    nouvelle_position = [particule.position[i] + particule.vitesse[i] for i in range(n)]
    rang = sorted(range(n), key=lambda x: nouvelle_position[x])
    particule.position = [rang.index(i) for i in range(n)]

def get_iterations(n):
    """Détermine le nombre maximal d'itérations en fonction du nombre de reines."""
    if n <= 10:
        return 500
    elif n <= 20:
        return 1000
    elif n <= 50:
        return 3000
    else:
        return 10_000  # Large n needs more iterations

def get_particles(n):
    """Détermine le nombre de particules en fonction du nombre de reines."""
    if n <= 10:
        return 50
    elif n <= 20:
        return 100
    elif n <= 50:
        return 200
    elif n <= 100:
        return 300
    else:
        return 600  

def pso_n_reines(n, progress_var=None):
    """Optimisation par essaim de particules pour le problème des n-reines."""
    max_iterations = get_iterations(n)
    nb_particules = get_particles(n)
    essaim = [Particule(n) for _ in range(nb_particules)]
    gBest = min(essaim, key=lambda p: p.score_pBest).position.copy()
    score_gBest = compter_conflits_total(gBest)

    for iteration in range(max_iterations):
        for particule in essaim:
            mise_a_jour_vitesse_et_position(particule, gBest)
            score_actuel = particule.fitness()
            
            if score_actuel < particule.score_pBest:
                particule.pBest = particule.position.copy()
                particule.score_pBest = score_actuel
                if score_actuel < score_gBest:
                    gBest = particule.position.copy()
                    score_gBest = score_actuel

        # Mise à jour de la barre de progression
        if progress_var:
            progress_var.set((iteration + 1) / max_iterations)
            root.update_idletasks()

        if score_gBest == 0:
            break

    return gBest, score_gBest, essaim, iteration + 1

def afficher_echiquier(solution, canvas, n):
    """Affiche la solution trouvée sur l'échiquier avec les indices des lignes et colonnes."""
    taille_case = 40
    canvas.delete("all")
    total_size = n * taille_case + 60
    canvas.config(scrollregion=(0, 0, total_size, total_size))

    canvas.update_idletasks()
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    offset_x = max((canvas_width - total_size) // 2, 0)
    offset_y = max((canvas_height - total_size) // 2, 0)

    # Dessin des cases et reines avec animation
    for i in range(n):
        for j in range(n):
            x1 = j * taille_case + 30 + offset_x
            y1 = i * taille_case + 30 + offset_y
            couleur = "#2E2E2E" if (i + j) % 2 == 0 else "#1C1C1C"
            canvas.create_rectangle(x1, y1, x1 + taille_case, y1 + taille_case, fill=couleur, outline="")

    # Ajouter les indices des lignes (côté gauche)
    for i in range(n):
        x1 = 0 + offset_x
        y1 = i * taille_case + 30 + offset_y
        canvas.create_text(x1 + taille_case // 2, y1 + taille_case // 2, text=str(i + 1), font=("Arial", 10), fill="white")

    # Ajouter les indices des colonnes (en bas)
    for j in range(n):
        x1 = j * taille_case + 30 + offset_x
        y1 = n * taille_case + 30 + offset_y
        canvas.create_text(x1 + taille_case // 2, y1 + taille_case // 2, text=str(j + 1), font=("Arial", 10), fill="white")

    # Animation progressive des reines
    for j in range(n):
        i = solution[j]
        x1 = j * taille_case + 30 + offset_x
        y1 = i * taille_case + 30 + offset_y
        canvas.create_text(x1 + taille_case//2, y1 + taille_case//2, text="♛", font=("Arial", 20), fill="red")
        root.update()
        root.after(200)

def afficher_table(essaim, gBest):
    """Affiche les pBest de chaque particule et le gBest dans un tableau."""
    for widget in table_content.winfo_children():
        widget.destroy()

    ctk.CTkLabel(table_content, text="Particule", width=10, fg_color="#1C1C1C", text_color="white").grid(row=0, column=0, padx=5, pady=5)
    ctk.CTkLabel(table_content, text="pBest", width=10, fg_color="#1C1C1C", text_color="white").grid(row=0, column=1, padx=5, pady=5)
    ctk.CTkLabel(table_content, text="Score", width=10, fg_color="#1C1C1C", text_color="white").grid(row=0, column=2, padx=5, pady=5)

    for i, particule in enumerate(essaim):
        bg_color = "#783f95" if particule.pBest == gBest else "#1C1C1C"
        ctk.CTkLabel(table_content, text=f"{i+1}", width=10, fg_color=bg_color, text_color="white").grid(row=i+1, column=0, padx=5, pady=5)
        ctk.CTkLabel(table_content, text=f"{particule.pBest}", width=10, fg_color=bg_color, text_color="white").grid(row=i+1, column=1, padx=5, pady=5)
        ctk.CTkLabel(table_content, text=f"{particule.score_pBest}", width=10, fg_color=bg_color, text_color="white").grid(row=i+1, column=2, padx=5, pady=5)

    ctk.CTkLabel(table_content, text="gBest", width=10, fg_color="#1C1C1C", text_color="white").grid(row=len(essaim)+1, column=0, padx=5, pady=5)
    ctk.CTkLabel(table_content, text=f"{gBest}", width=10, fg_color="#1C1C1C", text_color="white").grid(row=len(essaim)+1, column=1, padx=5, pady=5)

def resoudre_n_reines():
    """Résout le problème des n-reines et affiche le résultat."""
    try:
        n = int(entry.get())
        if n < 4:
            messagebox.showerror("Erreur", "n ≥ 4 requis.")
            return

        progress_var.set(0)
        start_time = time.time()
        solution, conflits, essaim, iterations = pso_n_reines(n, progress_var=progress_var)
        end_time = time.time()
        elapsed_time = end_time - start_time

        afficher_echiquier(solution, canvas, n)
        afficher_table(essaim, solution)
        resultat_label.configure(text=f"Solution : {solution}\nConflits : {conflits}\nTemps : {elapsed_time:.2f} secondes\nItérations : {iterations}")
    except ValueError:
        messagebox.showerror("Erreur", "Entrée invalide.")

# Interface graphique
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("n-Reines avec PSO")
root.geometry("1200x700")

# Cadre de contrôle
controls_frame = ctk.CTkFrame(root)
controls_frame.pack(pady=20)

# Entrée et bouton avec la même largeur
entry_width = 30  # Ajuste la largeur pour s'aligner avec le bouton
ctk.CTkLabel(controls_frame, text="Taille (n):").grid(row=0, column=0, padx=5)
entry = ctk.CTkEntry(controls_frame, width=entry_width)
entry.grid(row=0, column=1, padx=5)
bouton_resoudre = ctk.CTkButton(controls_frame, text="Résoudre", command=resoudre_n_reines, width=entry_width)
bouton_resoudre.grid(row=0, column=2, padx=5)

# Barre de progression
progress_var = ctk.DoubleVar()
progress_bar = ctk.CTkProgressBar(root, variable=progress_var)
progress_bar.pack(fill=ctk.X, padx=20, pady=10)

# Zone d'affichage principale
main_frame = ctk.CTkFrame(root)
main_frame.pack(fill=ctk.BOTH, expand=True)

# Canvas pour l'échiquier
canvas_frame = ctk.CTkFrame(main_frame)
canvas_frame.grid(row=0, column=0, sticky="nsew")
canvas = ctk.CTkCanvas(canvas_frame, bg="#1C1C1C", highlightthickness=0)
scroll_x = ctk.CTkScrollbar(canvas_frame, orientation=ctk.HORIZONTAL, command=canvas.xview)
scroll_y = ctk.CTkScrollbar(canvas_frame, orientation=ctk.VERTICAL, command=canvas.yview)
canvas.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
canvas_frame.grid_rowconfigure(0, weight=1)
canvas_frame.grid_columnconfigure(0, weight=1)
canvas.grid(row=0, column=0, sticky="nsew")
scroll_x.grid(row=1, column=0, sticky="ew")
scroll_y.grid(row=0, column=1, sticky="ns")

# Tableau pour afficher les pBest et gBest
table_frame = ctk.CTkFrame(main_frame, fg_color="#1C1C1C")
table_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
table_frame.grid_rowconfigure(0, weight=1)
table_frame.grid_columnconfigure(0, weight=1)

# Adding a canvas and scrollbar for the table frame
table_canvas = ctk.CTkCanvas(table_frame, bg="#1C1C1C")
table_canvas.grid(row=0, column=0, sticky="nsew")
table_scroll_y = ctk.CTkScrollbar(table_frame, orientation=ctk.VERTICAL, command=table_canvas.yview)
table_scroll_y.grid(row=0, column=1, sticky="ns")
table_canvas.configure(yscrollcommand=table_scroll_y.set)

# Frame inside the canvas to hold the table content
table_content = ctk.CTkFrame(table_canvas, fg_color="#1C1C1C")
table_canvas.create_window((0, 0), window=table_content, anchor="nw")

def update_table_scrollregion(event):
    table_canvas.configure(scrollregion=table_canvas.bbox("all"))

table_content.bind("<Configure>", update_table_scrollregion)

main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=3)
main_frame.grid_columnconfigure(1, weight=1)

# Résultat centré
resultat_label = ctk.CTkLabel(root, font=("Arial", 12), justify="center", anchor="center")
resultat_label.pack(pady=15, fill=ctk.X)

root.mainloop()