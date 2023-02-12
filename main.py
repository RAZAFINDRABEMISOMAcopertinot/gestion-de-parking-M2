# importer les modules necessaires
import re
import sys
import datetime
import pymysql
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QRegularExpression, QDate
from PyQt5.QtGui import QFont, QRegularExpressionValidator, QCursor
from stylesheet import style_sheet
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QTabWidget,
                             QGroupBox, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
                             QStackedLayout, QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit, QSpinBox)

# les models
from models import User, Chauffeur, Permis


# Base de donnée
class Database:
    def __init__(self):
        host = 'localhost'
        user = 'root'
        passwd = ''
        db = 'parking'

        self.con = pymysql.connect(host=host, user=user, passwd=passwd, db=db)

        self.cur = self.con.cursor()


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initializeUI()

    def initializeUI(self):
        """Cette fonction sert à initialiser l'application."""
        self.setMinimumSize(600, 700)
        self.setWindowTitle("Gestion de parking")
        self.setWindowIcon(QIcon("images/parking_logo.png"))
        self.setUpMainWindow()
        self.show()

    def setUpMainWindow(self):
        # Créer tab bar, les differents tabs, and set  object names pour les styler
        self.tab_bar = QTabWidget()
        self.login_tab = QWidget()
        self.login_tab.setObjectName("Tabs")

        self.tab_bar.addTab(self.login_tab, "Se connecter")

        self.loginTab()

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
        # self.email_edit.textEdited.connect()

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

            try:
                cred = User.checkPassword(password, hashed_password)
                if cred:
                    window.show()
                    log_window.close()
                else:
                    self.login_error_lbl.setText("Votre mot de passe est incorrecte.")
            except Exception as e:
                self.login_error_lbl.setText("Votre mot de passe est incorrecte.")

        else:
            self.login_error_lbl.setText("Assurez-vous que l'adresse votre email et mot de soient correctes.")

        print(user_data)


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

    def setUpMainWindow(self):
        """Créer et arranger les widgets dans la fenêtre principale ."""

        # Créer tab bar, les differents tabs, and set  object names pour les styler
        self.tab_bar = QTabWidget()
        # self.login_tab = QWidget()
        # self.login_tab.setObjectName("Tabs")
        self.register_tab = QWidget()
        self.register_tab.setObjectName("Tabs")

        self.management_tab = QWidget()
        self.management_tab.setObjectName("Tabs")

        self.tab_bar.addTab(self.register_tab, "S'inscrire")
        self.tab_bar.addTab(self.management_tab, "Acceuil")

        # Appeler les methodes qui contiennent les widgets pour chaque tabs
        self.registerTab()
        self.managementTab()

        # Ajouter les widgets à la fenêtre principale
        main_h_box = QHBoxLayout()
        main_h_box.addWidget(self.tab_bar)
        self.setLayout(main_h_box)

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

        menu_v_layout.addWidget(dashbord_button)
        menu_v_layout.addWidget(abonnement_button)
        menu_v_layout.addWidget(payement_button)

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

        # Tableau des utilisateurs
        user_table_title = QLabel("Les utilisateurs (05)")
        user_table = QTableWidget(3, 6)

        user_table.setHorizontalHeaderLabels(["ID", "FIRST_NAME", "LAST_NAME", "EMAIL", "PASSWORD", "ROLE"])

        user_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        for row in range(3):
            for col in range(6):
                item = QTableWidgetItem("Row {} Column {}".format(row + 1, col + 1))
                user_table.setItem(row, col, item)

        # Tableau des abonnés
        abonne_table_title = QLabel("Les chauffeurs abonnés (25)")
        abonne_table = QTableWidget(3, 6)
        abonne_table.setHorizontalHeaderLabels(["ID", "FIRST_NAME", "LAST_NAME", "EMAIL", "ABONNEMENT", "VEHICULE"])

        abonne_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        for row in range(3):
            for col in range(6):
                item = QTableWidgetItem("Row {} Column {}".format(row + 1, col + 1))
                abonne_table.setItem(row, col, item)

        # Tableau des véhicules
        vehicule_table_title = QLabel("Les véhicules (35)")
        vehicule_table = QTableWidget(3, 6)
        vehicule_table.setHorizontalHeaderLabels(
            ["ID", "MARQUE", "COULEUR", "NUM IMMATRICULE", "ABONNEMENT", "CHAUFFEUR"])

        vehicule_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        for row in range(3):
            for col in range(6):
                item = QTableWidgetItem("Row {} Column {}".format(row + 1, col + 1))
                vehicule_table.setItem(row, col, item)

        dhb_v_box = QVBoxLayout()

        dhb_v_box.addWidget(header_label)
        dhb_v_box.addWidget(user_table_title)
        dhb_v_box.addWidget(user_table)
        dhb_v_box.addWidget(abonne_table_title)
        dhb_v_box.addWidget(abonne_table)
        dhb_v_box.addWidget(vehicule_table_title)
        dhb_v_box.addWidget(vehicule_table)

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

        try:
            self.db = Database()
            self.db.cur.execute("SELECT PRENOM FROM chauffeurs ")
            chauff_data = self.db.cur.fetchall()
            chauff_list = [x[0] for x in chauff_data]
        except Exception as e:
            print(e.args[0])

        self.perm_titulair_combo = QComboBox()
        self.perm_titulair_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.perm_titulair_combo.addItems(chauff_list)



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

    def vehiculeTab(self):
        veh_v_box = QVBoxLayout()

        # formulaire pour les véhicules
        veh_gp = QGroupBox()
        veh_gp.setTitle("Information de véhicule")

        veh_form = QFormLayout()

        num_imm_edit = QLineEdit()
        num_imm_edit.setPlaceholderText("Numéro d'immatriculation")

        marque_edit = QLineEdit()
        marque_edit.setPlaceholderText("Marque de la voiture")

        couleur_edit = QLineEdit()
        couleur_edit.setPlaceholderText("Couleur de la voiture")

        chauffeur_combo = QComboBox()
        chauffeur_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        chauffeur_combo.addItems(["Kelly", "Coperty", "Safidy", "Blandine", "Eggla"])

        veh_form.addRow("Num IMM:", num_imm_edit)
        veh_form.addRow("Marque:", marque_edit)
        veh_form.addRow("Couleur:", couleur_edit)
        veh_form.addRow("Chauffeur", chauffeur_combo)

        veh_gp.setLayout(veh_form)

        # formulaire pour les véhicules
        carte_grise_gp = QGroupBox()
        carte_grise_gp.setTitle("Sa carte grise")

        carte_grise_form = QFormLayout()

        energy_edit = QLineEdit()
        energy_edit.setPlaceholderText("Energie utilisé")

        type_edit = QLineEdit()
        type_edit.setPlaceholderText("Type")

        numbre_place_edit = QLineEdit()
        numbre_place_edit.setPlaceholderText("Nombre de place")

        genre_edit = QLineEdit()
        genre_edit.setPlaceholderText("Genre")

        imm_combo = QComboBox()
        imm_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        imm_combo.addItems(["VUI", "VNI", "MHP", "CP"])

        date_circulation_edit = QDateEdit()
        date_circulation_edit.setDisplayFormat("MM / dd / yyyy")
        date_circulation_edit.setMaximumDate(QDate.currentDate())
        date_circulation_edit.setCalendarPopup(True)
        date_circulation_edit.setDate(QDate.currentDate())

        carte_grise_form.addRow("Energie:", energy_edit)
        carte_grise_form.addRow("Type:", type_edit)
        carte_grise_form.addRow("Nombre de place:", numbre_place_edit)
        carte_grise_form.addRow("Date de mise en circulation:", date_circulation_edit)

        carte_grise_gp.setLayout(carte_grise_form)

        # Boutton de soummission
        veh_add_btn = QPushButton("Ajouter")
        veh_add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        veh_v_box.addWidget(veh_gp)
        veh_v_box.addWidget(carte_grise_gp)
        veh_v_box.addWidget(veh_add_btn)

        self.creer_vehicule_tab.setLayout(veh_v_box)

    def abnTab(self):
        abn_v_box = QVBoxLayout()

        # formulaire pour les abonnements
        abn_gp = QGroupBox()
        abn_gp.setTitle("Ajouter un abonnement")

        abn_form = QFormLayout()

        type_abn_combo = QComboBox()
        type_abn_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        type_abn_combo.addItems(["PERMANENT", "JOUR", "NUIT"])

        prix_edit = QLineEdit()
        prix_edit.setPlaceholderText("Prix de l'abonnement en AR")

        # Boutton de soummission
        abn_add_btn = QPushButton("Ajouter")
        abn_add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        abn_form.addRow("Type:", type_abn_combo)
        abn_form.addRow("Prix:", prix_edit)
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

        abn_combo = QComboBox()
        abn_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        abn_combo.addItems(["PERMANENT", "JOUR", "NUIT"])

        chauffeur_combo = QComboBox()
        chauffeur_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        chauffeur_combo.addItems(["Kelly", "Coperty", "Safidy", "Blandine", "Eggla"])

        début_edit = QDateEdit()
        début_edit.setDisplayFormat("MM / dd / yyyy")
        début_edit.setMaximumDate(QDate.currentDate())
        début_edit.setCalendarPopup(True)
        début_edit.setDate(QDate.currentDate())

        fin_edit = QDateEdit()
        fin_edit.setDisplayFormat("MM / dd / yyyy")
        fin_edit.setMaximumDate(QDate.currentDate())
        fin_edit.setCalendarPopup(True)
        fin_edit.setDate(QDate.currentDate())

        payer_combo = QComboBox()
        payer_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        payer_combo.addItems(["NON", "OUI"])

        valide_combo = QComboBox()
        valide_combo.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        valide_combo.addItems(["NON", "OUI"])

        submit = QPushButton("Editer")
        submit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        carte_abn_form.addRow("Abonnement:", abn_combo)
        carte_abn_form.addRow("Chauffeur:", chauffeur_combo)
        carte_abn_form.addRow("Commencer le:", début_edit)
        carte_abn_form.addRow("Terminer le:", fin_edit)
        carte_abn_form.addRow("Validité:", valide_combo)
        carte_abn_form.addRow("Payé:", payer_combo)
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
                """, (chauffeur.getNom(), chauffeur.getPrénom(), chauffeur.getDateNaissance(), chauffeur.getLieuNaissance()))

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
                permis_obj.getCim(), permis_obj.getCategorie(), permis_obj.getValidité(), permis_obj.getChauffeur()))

                self.db.con.commit()

                self.perm_cim_idit.clear()

            else:
                print("Tous les champs sont tous obligatoires.")

        except Exception as e:
            print("tsssssss", e.args[0])





if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_sheet)
    window = MainWindow()
    log_window = LoginWindow()
    sys.exit(app.exec())
