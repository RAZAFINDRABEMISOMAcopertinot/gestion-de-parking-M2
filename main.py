# importer les modules necessaires
import os
import sys
import pymysql
from http import cookies
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QRegularExpression, QDate
from PyQt5.QtGui import QFont, QRegularExpressionValidator, QCursor
from stylesheet import style_sheet
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QTabWidget,
                             QGroupBox, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
                             QStackedLayout, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, QSpinBox,
                             QMessageBox)

# les models
from models import User, Chauffeur, Permis, Voiture, CarteGrise, Abonnement, CarteAbonnement


# Base de donnée
class Database:
    def __init__(self):
        host = 'localhost'
        user = 'root'
        passwd = ''
        db = 'parking'

        self.con = pymysql.connect(host=host, user=user, passwd=passwd, db=db, autocommit=True)

        self.cur = self.con.cursor()


# Login fonctionalité
# créer un cookie pour stoker l'authentification
session_cookie = cookies.SimpleCookie()
session_cookie["autheniticated"] = False
log_db_con = pymysql.connect(host='localhost', user='root', passwd='', db='parking')
log_db_cur = log_db_con.cursor()

try:
    log_db_cur.execute(""" SELECT * FROM authentication """)
    auth_data = log_db_cur.fetchone()
    if auth_data != None and auth_data[1] == 1:
        session_cookie["authenticated"] = True
    else:
        session_cookie["authenticated"] = False

except Exception as e:
    print(e.args[0])


class MainWindow(QWidget):
    def __init__(self):
        """ Constructeur de la classe Mainwindow """
        super().__init__()

        self.stack = QStackedLayout()
        self.initializeUI()

        self.stack.addWidget(self.dashboard_wdg())

        self.stack.addWidget(self.abonnement_wdg())

        self.stack.addWidget(self.payement_wdg())

    def initializeUI(self):
        """Cette fonction sert à initialiser l'application."""
        self.setMinimumSize(600, 700)
        self.setWindowTitle("Gestion de parking")
        self.setWindowIcon(QIcon("images/parking_logo.png"))
        self.setUpMainWindow()
        self.show()

    def setUpMainWindow(self):
        """Créer et arranger les widgets dans la fenêtre principale ."""

        # Créer tab bar, les differents tabs, and set  object names pour les styler
        self.tab_bar = QTabWidget()
        self.login_tab = QWidget()
        self.login_tab.setObjectName("Tabs")
        self.register_tab = QWidget()
        self.register_tab.setObjectName("Tabs")

        self.management_tab = QWidget()
        self.management_tab.setObjectName("Tabs")

        self.tab_bar.addTab(self.login_tab, "Se connecter")
        self.tab_bar.addTab(self.register_tab, "S'inscrire")
        self.tab_bar.addTab(self.management_tab, "Acceuil")

        # Cacher les deux tabs pour raison de sécurité
        if session_cookie.get("authenticated").value == str(True):
            self.tab_bar.setTabVisible(0, False)
            self.tab_bar.setTabVisible(1, True)
            self.tab_bar.setTabVisible(2, True)
            self.tab_bar.setCurrentIndex(2)
        else:
            self.tab_bar.setTabVisible(0, True)
            self.tab_bar.setTabVisible(1, False)
            self.tab_bar.setTabVisible(2, False)

        # Appeler les methodes qui contiennent les widgets pour chaque tabs
        self.loginTab()
        self.registerTab()
        self.managementTab()

        # Ajouter les widgets à la fenêtre principale
        main_h_box = QHBoxLayout()
        main_h_box.addWidget(self.tab_bar)
        self.setLayout(main_h_box)

    def loginTab(self):
        header_label = QLabel("Se connecter")
        header_label.setObjectName("Header")
        header_label.setFont(QFont("Arial", 18))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.email_login_edit = QLineEdit()
        self.email_login_edit.setPlaceholderText("<username>@<domain>.com")
        reg_opt = QRegularExpression()
        regex = QRegularExpression("\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[com]{3}\\b",
                                   reg_opt.PatternOption.CaseInsensitiveOption)
        self.email_login_edit.setValidator(QRegularExpressionValidator(regex))

        self.password_login_edit = QLineEdit()
        self.password_login_edit.setPlaceholderText("Mot de passe")
        self.password_login_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_error_lbl = QLabel()
        self.login_error_lbl.setObjectName("LoginError")

        submit_button = QPushButton("SOUMETTRE")
        submit_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        submit_button.clicked.connect(self.loginHandler)

        # Organiser les widgets et les layouts dans QFormLayout
        self.login_form = QFormLayout()
        self.login_form.setObjectName("LoginForm")
        self.login_form.setFieldGrowthPolicy(self.login_form.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.login_form.setFormAlignment(
            Qt.AlignmentFlag.AlignHCenter | \
            Qt.AlignmentFlag.AlignTop)
        self.login_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.login_form.addRow(header_label)
        self.login_form.addRow("Email:", self.email_login_edit)
        self.login_form.addRow("Mot de Passe:", self.password_login_edit)
        self.login_form.addRow(self.login_error_lbl)
        self.login_form.addRow(submit_button)

        # Ajouter le layout dans la fenêtre principale
        self.login_tab.setLayout(self.login_form)

    def loginHandler(self):
        email_log = self.email_login_edit.text()
        self.db = Database()
        self.db.cur.execute("SELECT * FROM utilisateurs WHERE EMAIL=%s", (email_log,))
        user_data = self.db.cur.fetchall()

        if user_data:
            password = self.password_login_edit.text()
            hashed_password = user_data[0][4]
            ut_id = user_data[0][0]

            try:
                cred = User.checkPassword(password, hashed_password)
                if cred:
                    self.db = Database()
                    self.db.cur.execute(""" INSERT INTO authentication (AUTH, UTILISATEUR_ID) VALUES (%s, %s)""",
                                        (True, ut_id))
                    self.db.con.commit()
                    self.tab_bar.setTabVisible(0, False)
                    self.tab_bar.setTabVisible(1, True)
                    self.tab_bar.setTabVisible(2, True)
                    self.email_login_edit.clear()
                    self.password_login_edit.clear()
                    self.tab_bar.setCurrentIndex(2)
                else:
                    self.login_error_lbl.setText("Votre mot de passe est incorrecte.")
            except Exception as e:
                self.login_error_lbl.setText("Votre mot de passe est incorrecte.", e.args[0])

        else:
            self.login_error_lbl.setText("Assurez-vous que l'adresse votre email et mot de soient correctes.")

        print(user_data)
        self.db.con.close()

    def registerTab(self):
        """Formulaire d'inscription."""

        header_label = QLabel("S'incrire")
        header_label.setObjectName("Header")
        header_label.setFont(QFont("Arial", 18))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Nom")

        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("Prénom")

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("<username>@<domain>.com")
        reg_opt = QRegularExpression()
        regex = QRegularExpression("\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[com]{3}\\b",
                                   reg_opt.PatternOption.CaseInsensitiveOption)
        self.email_edit.setValidator(QRegularExpressionValidator(regex))

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Mot de passe")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        self.roles_combo = QComboBox()
        self.roles_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.roles_combo.addItems(User.getRoles())

        submit_button = QPushButton("SOUMETTRE")
        submit_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        submit_button.clicked.connect(self.registerHandler)

        about_us = QLabel()
        about_us.setObjectName("AboutUs")
        about_us.setText("""
            <div>
                <h3>Un peu des mots sur nous</h3>
                <p>Le lorem ipsum est, en imprimerie, une suite de mots sans signification utilisée à titre <br>
                provisoire pour calibrer une mise en page, le texte définitif venant remplacer le faux-texte dès qu'il<br>
                 est prêt ou que la mise en page est achevée. Généralement, on utilise un texte en faux latin, le Lorem ipsum ou Lipsum.</p>
                 <p>Les services que nous vous proposons:
                <ol>
                    <li>Abonnement Permanent</li>
                    <li>Abonnement Jounalière</li>
                    <li>Abonnement Nuit</li>
                    <li>Et aussi parking temporaire</li>
                </ol>
            </div>
        """)

        # Organiser les widgets et les layouts dans QFormLayout
        register_form = QFormLayout()
        register_form.setObjectName("RegisterForm")
        register_form.setFieldGrowthPolicy(register_form.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        register_form.setFormAlignment(
            Qt.AlignmentFlag.AlignHCenter | \
            Qt.AlignmentFlag.AlignTop)
        register_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        register_form.addRow(header_label)
        register_form.addRow("Nom:", self.last_name_edit)
        register_form.addRow("Prénom:", self.first_name_edit)
        register_form.addRow("Email:", self.email_edit)
        register_form.addRow("Mot de Passe:", self.password_edit)
        register_form.addRow("Rôles:", self.roles_combo)
        register_form.addRow(submit_button)
        register_form.addRow(about_us)

        # Ajouter le layout dans la fenêtre principale
        self.register_tab.setLayout(register_form)

    def registerHandler(self):
        nom = self.last_name_edit.text()
        prénom = self.first_name_edit.text()
        email = self.email_edit.text()
        password = self.password_edit.text()
        rôle = self.roles_combo.currentText()

        if nom != "" and prénom != "" and email != "" and password != "":
            user = User(nom, prénom, email, rôle)

            user.setPassword(password)

            try:
                self.db = Database()
                self.db.cur.execute("""
                    INSERT INTO utilisateurs (NOM, PRENOM, EMAIL, MOTDEPASSE, RÔLE) VALUES   (%s, %s, %s, %s, %s)
                """, (user.getNom(), user.getPrénom(), user.getEmail(), user.getPassword(), user.getRôle()))

                self.db.con.commit()

                self.last_name_edit.clear()
                self.first_name_edit.clear()
                self.email_edit.clear()
                self.password_edit.clear()
            except Exception as e:
                print(e.args[0])

    def managementTab(self):
        management_box = QHBoxLayout()
        management_box.setObjectName("ManagementLayout")

        management_box.addWidget(self.left_side())
        management_box.addLayout(self.stack, 1)

        # Ajouter le layout dans la fenêtre principale
        self.management_tab.setLayout(management_box)

    def left_side(self):
        menu_gbox = QGroupBox()
        menu_gbox.setObjectName("SideMenu")
        menu_gbox.setTitle("BIEN VENUE DANS LE BACK OFFICE")

        menu_v_layout = QVBoxLayout()
        menu_v_layout.setAlignment(Qt.AlignTop)

        dashbord_button = QPushButton("Tableau de bord")
        dashbord_button.setObjectName("BackBut")
        dashbord_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        dashbord_button.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        abonnement_button = QPushButton("Gérer les abonnements")
        abonnement_button.setObjectName("BackBut")
        abonnement_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        abonnement_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        payement_button = QPushButton("Gérer les payements")
        payement_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        payement_button.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        payement_button.setObjectName("BackBut")

        decon_button = QPushButton("Se déconnecter")
        decon_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        decon_button.clicked.connect(self.deconexionHandler)
        decon_button.setObjectName("BackBut")

        menu_v_layout.addWidget(dashbord_button)
        menu_v_layout.addWidget(abonnement_button)
        menu_v_layout.addWidget(payement_button)
        menu_v_layout.addWidget(decon_button)

        menu_gbox.setLayout(menu_v_layout)

        return menu_gbox

    def dashboard_wdg(self):
        dhb_wdg = QWidget()

        # Le titre
        header_label = QLabel()
        header_label.setText("""<h6>Le tableau de bord</h6>""")
        header_label.setObjectName("Header")
        header_label.setFont(QFont("Arial", 18))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # LES UTILISATEURS

        # Obtenir tous les utilisateurs
        try:
            self.db = Database()
            self.db.cur.execute("SELECT * FROM utilisateurs")
            utilisateus_data = self.db.cur.fetchall()
        except Exception as e:
            print(e.args[0])

        # Tableau des utilisateurs
        user_table_title = QLabel("Les utilisateurs ({})".format(len(utilisateus_data)))
        user_table = QTableWidget(len(utilisateus_data), 6)

        user_table.setHorizontalHeaderLabels(["ID", "NOM", "PRENOM", "EMAIL", "MOT DE PASSE", "ROLE"])

        user_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        try:
            for row, utulisateur in enumerate(utilisateus_data):
                for col, valeur in enumerate(utulisateur):
                    item = QTableWidgetItem(valeur)
                    user_table.setItem(row, col, item)
        except Exception as e:
            print(e.args[0])

        # LES ABONNEES

        # Obtenir toutes les abonnées
        try:
            self.db = Database()
            self.db.cur.execute("SELECT * FROM chauffeurs")
            chauffeurs_data = self.db.cur.fetchall()
        except Exception as e:
            print(e.args[0])

        # Tableau des abonnés
        abonne_table_title = QLabel("Les chauffeurs abonnés ({})".format(len(chauffeurs_data)))
        abonne_table = QTableWidget(len(chauffeurs_data), 5)
        abonne_table.setHorizontalHeaderLabels(["ID", "NOM", "PRENOM", "DATE DE NAISSANCCE", "LIEU DE NAISSANCE"])

        abonne_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        try:
            for row, chauffeur in enumerate(chauffeurs_data):
                for col, valeur in enumerate(chauffeur):
                    item = QTableWidgetItem(str(valeur))
                    abonne_table.setItem(row, col, item)
        except Exception as e:
            print(e.args[0])


        # LES PERMIS

        # Obtenis tous les permis
        try:
            self.db = Database()
            self.db.cur.execute("SELECT * FROM permis")
            permis_data = self.db.cur.fetchall()
        except Exception as e:
            print(e.args[0])

        # Tableau de permis
        permis_table_title = QLabel("Les permis ({})".format(len(permis_data)))
        permis_table = QTableWidget(len(permis_data), 5)
        permis_table.setHorizontalHeaderLabels(["ID", "CIM", "CATEGORIE", "VALIDITE", "CHAUFFEUR_ID"])

        permis_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        try:
            for row, permis in enumerate(permis_data):
                for col, valeur in enumerate(permis):
                    item = QTableWidgetItem(str(valeur))
                    permis_table.setItem(row, col, item)
        except Exception as e:
            print(e.args[0])

        # LES VOITURES

        # Obtenir tous les voitures
        try:
            self.db = Database()
            self.db.cur.execute("SELECT * FROM voitures")
            voitures_data = self.db.cur.fetchall()
        except Exception as e:
            print(e.args[0])

        # Tableau des véhicules
        vehicule_table_title = QLabel("Les véhicules ({})".format(len(voitures_data)))
        vehicule_table = QTableWidget(len(voitures_data), 6)
        vehicule_table.setHorizontalHeaderLabels(
            ["ID", "NUM IMMATRICULE", "MARQUE", "COULEUR", "DANS LE PACKING", "CHAUFFEUR_ID"])

        vehicule_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        for row, voiture in enumerate(voitures_data):
            for col, valeur in enumerate(voiture):
                item = QTableWidgetItem(str(valeur))
                vehicule_table.setItem(row, col, item)

        # LES CARTES GRISES

        # Obtenir toutes les cartes grises

        try:
            self.db = Database()
            self.db.cur.execute("SELECT * FROM carte_grises")
            cartes_grises_data = self.db.cur.fetchall()
        except Exception as e:
            print(e.args[0])

        # Tableau de cartes grises

        carte_grise_table_title = QLabel("Les cartes grises des véhicules ({})".format(len(cartes_grises_data)))
        carte_grise_table = QTableWidget(len(cartes_grises_data), 7)
        carte_grise_table.setHorizontalHeaderLabels(
            ["ID", "ENERGIE UTILISE", "TYPE", "NOMBRE DE PLACE", "IMMATRICULATION", "DATE DE MISE EN CIRCULATION", "VOITURE_ID"])

        carte_grise_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        for row, carte_grise in enumerate(cartes_grises_data):
            for col, valeur in enumerate(carte_grise):
                item = QTableWidgetItem(str(valeur))
                carte_grise_table.setItem(row, col, item)

        dhb_v_box = QVBoxLayout()

        dhb_v_box.addWidget(header_label)
        dhb_v_box.addWidget(user_table_title)
        dhb_v_box.addWidget(user_table)
        dhb_v_box.addWidget(abonne_table_title)
        dhb_v_box.addWidget(abonne_table)
        dhb_v_box.addWidget(permis_table_title)
        dhb_v_box.addWidget(permis_table)
        dhb_v_box.addWidget(vehicule_table_title)
        dhb_v_box.addWidget(vehicule_table)
        dhb_v_box.addWidget(carte_grise_table_title)
        dhb_v_box.addWidget(carte_grise_table)

        dhb_wdg.setLayout(dhb_v_box)

        return dhb_wdg

    def abonnement_wdg(self):
        abn_wdg = QWidget()
        header_label = QLabel()
        header_label.setObjectName("Header")
        header_label.setFont(QFont("Arial", 18))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setText("""<h6>Gérer les abonnements</h6>""")

        # Créer le menu de la gestion du parking
        abn_main_tab = QTabWidget()

        self.creer_chauffeur_tab = QWidget()
        self.creer_chauffeur_tab.setObjectName("Tabs")

        self.creer_vehicule_tab = QWidget()
        self.creer_vehicule_tab.setObjectName("Tabs")

        self.creer_abn_tab = QWidget()
        self.creer_abn_tab.setObjectName("Tabs")

        self.creer_carte_abn_tab = QWidget()
        self.creer_carte_abn_tab.setObjectName("Tabs")

        abn_main_tab.addTab(self.creer_chauffeur_tab, "Ajouter un chauffeur")
        abn_main_tab.addTab(self.creer_vehicule_tab, "Ajouter un véhicule")
        abn_main_tab.addTab(self.creer_carte_abn_tab, "Editer un carte d'abonnement")
        abn_main_tab.addTab(self.creer_abn_tab, "Créer un abonnement")

        # Appeler les methodes qui contiennent les widgets pour chaque tabs
        self.chauffeurTab()
        self.vehiculeTab()
        self.carteAbnTab()
        self.abnTab()

        abn_v_box = QVBoxLayout()

        abn_v_box.addWidget(header_label)
        abn_v_box.addWidget(abn_main_tab)

        abn_wdg.setLayout(abn_v_box)
        return abn_wdg

    def payement_wdg(self):
        return QPushButton("Gerer les payements")

    def chauffeurTab(self):

        chauff_v_box = QVBoxLayout()

        # formulaire pour les chauffeur
        chauff_gp = QGroupBox()
        chauff_gp.setTitle("Information de Chauffeur")

        chauff_form = QFormLayout()
        self.chauff_nom_edit = QLineEdit()
        self.chauff_nom_edit.setPlaceholderText("Nom")

        self.chauff_prénom_edit = QLineEdit()
        self.chauff_prénom_edit.setPlaceholderText("Prénom")

        self.chauff_date_naissance_edit = QDateEdit()
        self.chauff_date_naissance_edit.setDisplayFormat("MM / dd / yyyy")
        self.chauff_date_naissance_edit.setMaximumDate(QDate.currentDate())
        self.chauff_date_naissance_edit.setCalendarPopup(True)
        self.chauff_date_naissance_edit.setDate(QDate.currentDate())

        self.chauff_lieu_naissance_edit = QLineEdit()
        self.chauff_lieu_naissance_edit.setPlaceholderText("Lieu de naissance")

        # Boutton de soummission pour chauffeur
        self.chauff_add_btn = QPushButton("Ajouter")
        self.chauff_add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.chauff_add_btn.clicked.connect(self.chauffeurRegisterHandler)
        self.chauff_add_btn.clicked.connect(self.reloadWindow)

        chauff_form.addRow("Nom:", self.chauff_nom_edit)
        chauff_form.addRow("Prénom:", self.chauff_prénom_edit)
        chauff_form.addRow("Date de naissance:", self.chauff_date_naissance_edit)
        chauff_form.addRow("Lieu de naissance:", self.chauff_lieu_naissance_edit)
        chauff_form.addRow(self.chauff_add_btn)

        chauff_gp.setLayout(chauff_form)

        # formulaire pour leur permis
        permis_gp = QGroupBox()
        permis_gp.setTitle("Son permis de conduit")

        permis_form = QFormLayout()

        self.perm_cim_idit = QLineEdit()
        self.perm_cim_idit.setPlaceholderText("CIM")

        self.perm_category_idit = QComboBox()
        self.perm_category_idit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.perm_category_idit.addItems(Permis.getCatgories())

        self.perm_validation_edit = QDateEdit()
        self.perm_validation_edit.setDisplayFormat("MM/dd/yyyy")
        start_date = QDate.currentDate()
        self.perm_validation_edit.setMaximumDate(start_date.addYears(5))
        self.perm_validation_edit.setCalendarPopup(True)
        self.perm_validation_edit.setDate(QDate.currentDate())

        self.perm_titulair_combo = QComboBox()
        self.perm_titulair_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.perm_titulair_combo.addItems(self.recupererPénomChauffeur())

        # Boutton de soummission pour permis
        self.perm_add_btn = QPushButton("Ajouter")
        self.perm_add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.perm_add_btn.clicked.connect(self.permisRegisterHandler)

        permis_form.addRow("CIM:", self.perm_cim_idit)
        permis_form.addRow("CATEGORY:", self.perm_category_idit)
        permis_form.addRow("Valable jusque le:", self.perm_validation_edit)
        permis_form.addRow("Titulaire:", self.perm_titulair_combo)
        permis_form.addRow(self.perm_add_btn)

        permis_gp.setLayout(permis_form)

        chauff_v_box.addWidget(chauff_gp)
        chauff_v_box.addWidget(permis_gp)

        self.creer_chauffeur_tab.setLayout(chauff_v_box)

    def recupererPénomChauffeur(self):
        try:
            while True:
                self.db = Database()
                self.db.cur.execute("SELECT PRENOM FROM chauffeurs ")
                chauff_data = self.db.cur.fetchall()
                chauff_list = [x[0] for x in chauff_data]
                return chauff_list
                self.db.con.close()
        except Exception as e:
            print(e.args[0])

    def recupererLesVehicules(self):
        try:
            while True:
                self.db = Database()
                self.db.cur.execute("SELECT NUM_IMM FROM voitures ")
                voiture_data = self.db.cur.fetchall()
                voiture_list = [x[0] for x in voiture_data]
                return voiture_list
                self.db.con.close()
        except Exception as e:
            print(e.args[0])

    def vehiculeTab(self):
        veh_v_box = QVBoxLayout()

        # formulaire pour les véhicules
        veh_gp = QGroupBox()
        veh_gp.setTitle("Information de véhicule")

        veh_form = QFormLayout()

        self.veh_num_imm_edit = QLineEdit()
        self.veh_num_imm_edit.setPlaceholderText("Numéro d'immatriculation")

        self.veh_marque_edit = QLineEdit()
        self.veh_marque_edit.setPlaceholderText("Marque de la voiture")

        self.veh_couleur_edit = QLineEdit()
        self.veh_couleur_edit.setPlaceholderText("Couleur de la voiture")

        self.veh_chauffeur_combo = QComboBox()
        self.veh_chauffeur_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.veh_chauffeur_combo.addItems(self.recupererPénomChauffeur())

        # Boutton de soummission pour une véhicule
        veh_add_btn = QPushButton("Ajouter")
        veh_add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        veh_add_btn.clicked.connect(self.vehiculeRegisterHandler)
        veh_add_btn.clicked.connect(self.reloadWindow)

        veh_form.addRow("Num IMM:", self.veh_num_imm_edit)
        veh_form.addRow("Marque:", self.veh_marque_edit)
        veh_form.addRow("Couleur:", self.veh_couleur_edit)
        veh_form.addRow("Chauffeur", self.veh_chauffeur_combo)
        veh_form.addRow(veh_add_btn)

        veh_gp.setLayout(veh_form)

        # formulaire pour les véhicules
        carte_grise_gp = QGroupBox()
        carte_grise_gp.setTitle("Sa carte grise")

        carte_grise_form = QFormLayout()

        self.energy_edit = QLineEdit()
        self.energy_edit.setPlaceholderText("Energie utilisé")

        self.type_edit = QLineEdit()
        self.type_edit.setPlaceholderText("Type")

        self.numbre_place_edit = QLineEdit()
        self.numbre_place_edit.setPlaceholderText("Nombre de place")

        self.genre_edit = QLineEdit()
        self.genre_edit.setPlaceholderText("Genre")

        self.imm_combo = QComboBox()
        self.imm_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.imm_combo.addItems(CarteGrise.getImmatriculation())

        self.date_circulation_edit = QDateEdit()
        self.date_circulation_edit.setDisplayFormat("MM / dd / yyyy")
        self.date_circulation_edit.setMaximumDate(QDate.currentDate())
        self.date_circulation_edit.setCalendarPopup(True)
        self.date_circulation_edit.setDate(QDate.currentDate())

        self.carte_titulair_combo = QComboBox()
        self.carte_titulair_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.carte_titulair_combo.addItems(self.recupererLesVehicules())

        # Boutton de soummission pour une carte grise
        carte_grise_add_btn = QPushButton("Ajouter")
        carte_grise_add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        carte_grise_add_btn.clicked.connect(self.carteGriseRegisterHandler)

        carte_grise_form.addRow("Energie:", self.energy_edit)
        carte_grise_form.addRow("Type:", self.type_edit)
        carte_grise_form.addRow("Nombre de place:", self.numbre_place_edit)
        carte_grise_form.addRow("Immatriculation:", self.imm_combo)
        carte_grise_form.addRow("Date de mise en circulation:", self.date_circulation_edit)
        carte_grise_form.addRow("Apartient à:", self.carte_titulair_combo)
        carte_grise_form.addRow(carte_grise_add_btn)

        carte_grise_gp.setLayout(carte_grise_form)

        veh_v_box.addWidget(veh_gp)
        veh_v_box.addWidget(carte_grise_gp)

        self.creer_vehicule_tab.setLayout(veh_v_box)

    def abnTab(self):
        abn_v_box = QVBoxLayout()

        # formulaire pour les abonnements
        abn_gp = QGroupBox()
        abn_gp.setTitle("Ajouter un abonnement")

        abn_form = QFormLayout()

        self.type_abn_combo = QComboBox()
        self.type_abn_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.type_abn_combo.addItems(Abonnement.getAllTypes())

        self.prix_edit = QLineEdit()
        self.prix_edit.setPlaceholderText("Prix de l'abonnement en AR")

        # Boutton de soummission
        abn_add_btn = QPushButton("Ajouter")
        abn_add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        abn_add_btn.clicked.connect(self.addAbonnementHandler)

        abn_form.addRow("Type:", self.type_abn_combo)
        abn_form.addRow("Prix:", self.prix_edit)
        abn_form.addRow(abn_add_btn)

        # Listes de abonnemnts dispo
        abn_dispo_gp = QGroupBox()
        abn_dispo_gp.setTitle("Les abonnements disponnibles")


        # Tableau des abonnements disponibles
        abn_table = QTableWidget(3, 4)
        abn_table.setHorizontalHeaderLabels(["ID", "TYPE", "PRIX", "DESCRIPTION"])

        abn_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        for row in range(3):
            for col in range(4):
                item = QTableWidgetItem("Row {} Column {}".format(row + 1, col + 1))
                abn_table.setItem(row, col, item)

        abn_gp.setLayout(abn_form)

        # abn_dispo_gp.setLayout(abn_table)
        abn_v_box.addWidget(abn_gp)
        abn_v_box.addWidget(abn_table)

        self.creer_abn_tab.setLayout(abn_v_box)

    def carteAbnTab(self):
        carte_abn_v_box = QVBoxLayout()

        # formulaire pour les abonnements
        carte_abn_gp = QGroupBox()
        carte_abn_gp.setTitle("Un carte d'abonnement")

        carte_abn_form = QFormLayout()

        self.crtabn_abn_combo = QComboBox()
        self.crtabn_abn_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.crtabn_abn_combo.addItems(["PERMANENT", "JOUR", "NUIT"])

        self.crtabn_chauffeur_combo = QComboBox()
        self.crtabn_chauffeur_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.crtabn_chauffeur_combo.addItems(self.recupererPénomChauffeur())

        self.crtabn_début_edit = QDateEdit()
        self.crtabn_début_edit.setDisplayFormat("MM / dd / yyyy")
        self.crtabn_début_edit.setMaximumDate(QDate.currentDate())
        self.crtabn_début_edit.setCalendarPopup(True)
        self.crtabn_début_edit.setDate(QDate.currentDate())

        self.crtabn_fin_edit = QDateEdit()
        self.crtabn_fin_edit.setDisplayFormat("MM / dd / yyyy")
        start_date = QDate.currentDate()
        self.crtabn_fin_edit.setMaximumDate(start_date.addYears(5))
        self.crtabn_fin_edit.setCalendarPopup(True)
        self.crtabn_fin_edit.setDate(QDate.currentDate())

        self.crtabn_payer_combo = QComboBox()
        self.crtabn_payer_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.crtabn_payer_combo.addItems(CarteAbonnement.getDejaPayer())

        self.crtabn_valide_combo = QComboBox()
        self.crtabn_valide_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.crtabn_valide_combo.addItems(CarteAbonnement.getEncoreValide())

        submit = QPushButton("Editer")
        submit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        submit.clicked.connect(self.carteAbnHandler)

        carte_abn_form.addRow("Abonnement:", self.crtabn_abn_combo)
        carte_abn_form.addRow("Chauffeur:", self.crtabn_chauffeur_combo)
        carte_abn_form.addRow("Commencer le:", self.crtabn_début_edit)
        carte_abn_form.addRow("Terminer le:", self.crtabn_fin_edit)
        carte_abn_form.addRow("Validité:", self.crtabn_valide_combo)
        carte_abn_form.addRow("Payé:", self.crtabn_payer_combo)
        carte_abn_form.addRow(submit)

        carte_abn_gp.setLayout(carte_abn_form)

        carte_abn_v_box.addWidget(carte_abn_gp)

        self.creer_carte_abn_tab.setLayout(carte_abn_v_box)

    def chauffeurRegisterHandler(self):
        nom = self.chauff_nom_edit.text()
        prénom = self.chauff_prénom_edit.text()
        date_naissance = self.chauff_date_naissance_edit.text()
        lieu_naissance = self.chauff_lieu_naissance_edit.text()

        if nom != "" and prénom != "" and date_naissance != "" and lieu_naissance != "":
            chauffeur = Chauffeur(nom, prénom, lieu_naissance)

            try:
                chauffeur.setDateNaissance(date_naissance)
            except Exception as e:
                print(e.args[0])

            try:
                self.db = Database()
                self.db.cur.execute("""
                    INSERT INTO chauffeurs (NOM, PRENOM, DATE_NAISSANCE, LIEU_NAISSANCE) VALUES   (%s, %s, %s, %s)
                """, (
                    chauffeur.getNom(), chauffeur.getPrénom(), chauffeur.getDateNaissance(),
                    chauffeur.getLieuNaissance()))

                self.db.con.commit()

                self.chauff_nom_edit.clear()
                self.chauff_prénom_edit.clear()
                self.chauff_lieu_naissance_edit.clear()
            except Exception as e:
                print("Tsy nanjary", e.args[0])
        else:
            print("Les champs sont tous obligatoires")

    def permisRegisterHandler(self):
        cim = self.perm_cim_idit.text()
        category = self.perm_category_idit.currentText()
        titulair = self.perm_titulair_combo.currentText()
        val = self.perm_validation_edit.text()
        try:
            self.db = Database()
            self.db.cur.execute("SELECT * FROM chauffeurs WHERE PRENOM=%s", (titulair,))
            chauff_data = self.db.cur.fetchall()
            chauff_id = int(chauff_data[0][0])
            if cim != "" and category != "" and chauff_id != "":
                permis_obj = Permis(cim, category, chauff_id)
                permis_obj.setValidité(val)

                self.db = Database()
                self.db.cur.execute("""
                                    INSERT INTO permis (CIM, CATEGORIE, VALIDITE, CHAUFFEUR_ID) VALUES   (%s, %s, %s, %s)
                                """, (
                    permis_obj.getCim(), permis_obj.getCategorie(), permis_obj.getValidité(),
                    permis_obj.getChauffeur()))

                self.db.con.commit()

                self.perm_cim_idit.clear()

            else:
                print("Tous les champs sont tous obligatoires.")

        except Exception as e:
            print("tsssssss", e.args[0])

    def vehiculeRegisterHandler(self):
        num_im = self.veh_num_imm_edit.text()
        marque = self.veh_marque_edit.text()
        couleur = self.veh_couleur_edit.text()
        veh_chauffeur = self.veh_chauffeur_combo.currentText()
        try:
            self.db = Database()
            self.db.cur.execute("SELECT * FROM chauffeurs WHERE PRENOM=%s", (veh_chauffeur,))
            chauff_data = self.db.cur.fetchall()
            chauff_id = int(chauff_data[0][0])

            if num_im != "" and marque != "" and couleur != "" and chauff_id != "":
                voiture_obj = Voiture(num_im, marque, couleur, chauff_id)

                self.db = Database()
                self.db.cur.execute("""
                                    INSERT INTO voitures (NUM_IMM, MARQUE, COULEUR, CHAUFFEUR_ID) VALUES   (%s, %s, %s, %s)
                                """, (
                    voiture_obj.getNumImm(), voiture_obj.getMarque(), voiture_obj.getCouleur(),
                    voiture_obj.getChauffeur()))

                self.db.con.commit()

                self.veh_num_imm_edit.clear()
                self.veh_marque_edit.clear()
                self.veh_couleur_edit.clear()

            else:
                print("Tous les champs sont obligatoires.")

        except Exception as e:
            print(e.args[0])

    def carteGriseRegisterHandler(self):
        energie = self.energy_edit.text()
        type = self.type_edit.text()
        nbr_place = self.numbre_place_edit.text()
        imm = self.imm_combo.currentText()
        date_de_m_cir = self.date_circulation_edit.text()
        veh_num_imm = self.carte_titulair_combo.currentText()

        try:
            self.db = Database()
            self.db.cur.execute("SELECT * FROM voitures WHERE NUM_IMM=%s", (veh_num_imm,))
            veh_data = self.db.cur.fetchall()
            veh_id = int(veh_data[0][0])
        except Exception as e:
            print(e.args[0])

        if energie != "" and type != "" and nbr_place != "" and imm != "" and date_de_m_cir != "":
            carte_grise = CarteGrise(energie, type, nbr_place, imm, veh_id)
            carte_grise.setDateDeCirculation(date_de_m_cir)

            print(carte_grise.getEnergie(), carte_grise.getType(), carte_grise.getNomberPlace(), imm,
                  carte_grise.getDateDeCirculation(), carte_grise.getVehicule())

            try:
                self.db = Database()
                self.db.cur.execute("""
                                       INSERT INTO carte_grises (ENERGIE, TYPE, NUMBRE_PLACE, IMMATRICULATION, DATE_DE_CIRCULATION, VOITURE_ID) VALUES   (%s, %s, %s, %s, %s, %s)
                   """, (carte_grise.getEnergie(), carte_grise.getType(), carte_grise.getNomberPlace(), imm,
                         carte_grise.getDateDeCirculation(), carte_grise.getVehicule()))
                self.db.con.commit()

                self.energy_edit.clear()
                self.type_edit.clear()
                self.numbre_place_edit.clear()

            except Exception as e:
                print(e.args[0])

    def addAbonnementHandler(self):
        type = self.type_abn_combo.currentText()
        prix = self.prix_edit.text()

        if type != "" and prix != "":
            abonnement = Abonnement(type, prix)
            try:
                self.db = Database()
                self.db.cur.execute(""" INSERT INTO abonnements (TYPE, PRIX) VALUES (%s, %s)""",
                                    (abonnement.getType(), abonnement.getPrix()))
                self.db.con.commit()
                self.db.con.close()
                self.prix_edit.clear()
            except Exception as e:
                print(e.args[0])

    def carteAbnHandler(self):
        abonnement_type = self.crtabn_abn_combo.currentText()
        chauffeur = self.crtabn_chauffeur_combo.currentText()
        debut_abn = self.crtabn_début_edit.text()
        fin_abn = self.crtabn_fin_edit.text()
        validité_abn = self.crtabn_valide_combo.currentText()
        payement = self.crtabn_payer_combo.currentText()

        if abonnement_type != "" and chauffeur != "" and debut_abn != "" and fin_abn != "" and validité_abn != "" and payement != "":
            if validité_abn == "OUI":
                validité_abn = True
            else:
                validité_abn = False

            if payement == "OUI":
                payement = True
            else:
                payement = False

            # Obtenir le chauffeur
            try:
                self.db = Database()
                self.db.cur.execute("SELECT * FROM chauffeurs WHERE PRENOM=%s", (chauffeur,))
                chauffeur_data = self.db.cur.fetchone()
                print(chauffeur_data)
                chauffeur_id = chauffeur_data[0]
                self.db.cur.close()
                self.db.con.close()
            except Exception as e:
                print(e.args[0])

            # Obtenir le type d'abonnement qu'il va faire
            try:
                self.db = Database()
                self.db.cur.execute("SELECT * FROM abonnements WHERE TYPE=%s", (abonnement_type,))
                abonnement_data = self.db.cur.fetchone()
                abonnement_id = abonnement_data[0]
                self.db.cur.close()
                self.db.con.close()
            except Exception as e:
                print(e.args[0])

            carteAbonnement = CarteAbonnement(abonnement_id, chauffeur_id, payement, validité_abn)
            carteAbonnement.setDebut(debut_abn)
            carteAbonnement.setFin(fin_abn)

            # Editer un carte d'abonnement
            try:
                self.db = Database()
                self.db.cur.execute("""
                    INSERT INTO carte_abonnements (ID_ABONNEMENT, ID_CHAUFEUR, DEJA_PAYER, ENCORE_VALIDE, DEBUT, FIN) VALUES (%s, %s, %s, %s, %s, %s)
                """, (carteAbonnement.getAbonnement(), carteAbonnement.getChauffeur(), carteAbonnement.getPayer(),
                      carteAbonnement.getValide(), carteAbonnement.getDebut(), carteAbonnement.getFin()))
                self.db.con.commit()
                self.db.con.close()
                QMessageBox.information(None, 'Carte d\'abonnement', 'Elle a bien éditer.')
            except Exception as e:
                print(e.args[0])

    def reloadWindow(self):
        QApplication.quit()
        try:
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            print(e.args[0])
        self.tab_bar.setCurrentIndex(2)

    def deconexionHandler(self):
        try:
            self.db = Database()
            self.db.cur.execute("""DELETE FROM authentication""")
            self.db.cur.close()
            self.db.con.commit()
            self.tab_bar.setTabVisible(0, True)
            self.tab_bar.setTabVisible(1, False)
            self.tab_bar.setTabVisible(2, False)
        except Exception as e:
            print(e.args[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    window = MainWindow()
    sys.exit(app.exec())
