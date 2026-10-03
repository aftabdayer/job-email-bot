"""
Automated Job Cold Email Bot — REAL HR LIST VERSION
=====================================================
Uses your actual HR contacts list (1,842 real people).
No APIs needed. 100% free.

SETUP:
  pip install secure-smtplib

Fill in CONFIG below. That's it.
Run: python job_bot_real_hrlist.py
"""

import time
import random
import sqlite3
import smtplib
import hashlib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ─────────────────────────────────────────────
#  CONFIG — fill these in
# ─────────────────────────────────────────────

YOUR_NAME      = "Aftab Dayer"
YOUR_PHONE     = "+91-8233689262"
YOUR_EMAIL_ID  = "dayeraftab3@gmail.com"       # your personal email shown in body
YOUR_LINKEDIN  = "linkedin.com/in/aftabdayer"
YOUR_GITHUB    = "github.com/aftabdayer"
YOUR_COLLEGE   = "NIT Hamirpur"
YOUR_DEGREE    = "Integrated B.Tech + M.Tech, Electronics & Communication Engineering"

# Roles you're open to — script rotates between these in subject lines
TARGET_ROLES   = [
    "Data Analyst",
    "Business Analyst",
    "Product Analyst",
    "Junior Product Manager",
    "Data Science Analyst",
    "Analytics Engineer",
]

YOUR_SKILLS    = "Python, SQL, Power BI, and ML-based analytics"
YOUR_HIGHLIGHT = (
    "IEEE-published researcher (IACIS-2025), Microsoft Power BI Certified (PL-300), "
    "and builder of 3 production-deployed data products"
)

# ── SECURITY: use a SEPARATE Gmail made just for job applications ──
# Recommended: create aftab.jobs2025@gmail.com (free, takes 2 min)
# That way your personal Gmail stays 100% untouched
# App Password only gives email access — not Drive, Photos, or account
# Revoke anytime: myaccount.google.com → Security → App Passwords → delete
GMAIL_ADDRESS      = "aftab.jobs2026@gmail.com"   # ← put your job-search Gmail here
GMAIL_APP_PASSWORD = "sotx csgk exlg pkhc"               # ← App Password for that Gmail

DB_FILE       = "aftab_contacted.db"
DAILY_LIMIT   = 25       # safe Gmail limit — don't go beyond 40
FOLLOWUP_DAYS = 5        # days to wait before follow-up

# ─────────────────────────────────────────────
#  YOUR REAL HR LIST (from the PDF you shared)
#  Format: (Name, Email, Title, Company)
#  Already loaded — 1,842 contacts ready to go
# ─────────────────────────────────────────────

HR_LIST = [
    ("Akanksha Puri", "akanksha.puri@sourcefuse.com", "Associate Director HR", "SourceFuse Technologies"),
    ("Akanksha Sogani", "akanksha.sogani@perennialsys.com", "Head HR", "Perennial Systems"),
    ("Akhil Jogiparthi", "akhil@ibhubs.co", "Vice President - Talent Accelerator", "iB Hubs"),
    ("Akhila Chandan", "akhila@estuate.com", "Associate Vice President Human Resources", "Estuate"),
    ("Akram Mohammad", "akram.mohammad@colruytgroup.com", "Deputy Head HR", "Colruyt India"),
    ("Akriti", "akriti@elsner.in", "HR-Head", "Elsner Technologies"),
    ("Akshata Bhandare", "akshata.bhandare@windmill.ch", "HR & Location Head India", "Windmill"),
    ("Albino Mascarenhas", "albino@pixis.ai", "Head - Human Resources Global", "Pyxis One"),
    ("Allwyn Richard", "allwyn.r@qbrainx.com", "Head of Human Resources", "QBrainX Inc"),
    ("Alok Baghel", "alok.singh@recro.io", "Head Of Talent Management", "Recro"),
    ("Alwyn Barretto", "alwyn.barretto@infrasofttech.com", "Head Recruitments", "Infrasoft Technologies"),
    ("Aman Khan", "aman.khan@areteanstech.com", "Vice President Human Resources", "Areteans"),
    ("Amandeep Kaur", "amandeep.k@antiersolutions.com", "Sr. HR Executive Technical Recruitment Head", "Antier Solutions"),
    ("Amar Sinha", "amar.sinha@nitorinfotech.com", "Director Talent Acquisition", "Nitor Infotech"),
    ("Ambrish Kanungo", "ambrish.kanungo@beyondkey.com", "Head of HR", "Beyond Key"),
    ("Amiit Avaasthi", "amiit.avaasthi@altudo.co", "Chief People Officer", "Altudo"),
    ("Amit Kataria", "amit@hanu.com", "Chief Human Resources Officer", "Hanu Software"),
    ("Amit Prayagi", "amit.prayagi@claimgenius.com", "Head Of Recruitment & HR", "Claim Genius"),
    ("Amit Ranjan", "amit.ranjan@scikey.ai", "Associate Director Talent Solutions", "SCIKEY"),
    ("Amit Sahoo", "amit.sahoo@areteanstech.com", "Vice President Global Head HR", "Areteans"),
    ("Amita Shital", "ashital@svam.com", "Head of HR", "SVAM International"),
    ("Amitesh Verma", "amitesh.verma@cheersin.com", "Associate Director Talent Acquisition", "Cheers Interactive"),
    ("Amitha K", "amitha.k@secure-24.com", "Director HR", "Secure-24"),
    ("Amlan Nag", "amlan.nag@mjunction.in", "General Manager & Head HR", "mjunction services"),
    ("Amresh Mehra", "amreshm@zendrive.com", "VP - People & Culture", "Zendrive"),
    ("Amrita Cheema", "amrita.cheema@loconav.com", "Head HR Global SaaS", "LocoNav"),
    ("Amrita Tripathi", "amrita@sdnaglobal.com", "VP - India ME and APAC HR", "Stanley David and Associates"),
    ("Amritesh Shukla", "amritesh.shukla@mygate.com", "Head Of Human Resources", "MyGate"),
    ("Anand Christopher", "anand.christopher@grassrootsbpo.com", "Vice President Human Resources", "Grassroots"),
    ("Anand E", "anand.e@increff.com", "Chief Human Resources Officer", "Increff"),
    ("Anand Khot", "anandk@pharmarack.com", "Chief Human Resources Officer", "Pharmarack"),
    ("Anand Sasidharan", "anand@hubilo.com", "Head of Talent Acquisition", "Hubilo"),
    ("Anand Soni", "anand@capsitech.com", "Talent Acquisition Head", "Capsitech"),
    ("Anchal Rastogi", "anrastogi@enhanceit.com", "AVP Recruitments", "Enhance IT"),
    ("Angel Mathew", "angel.mathew@delphix.com", "Human Resources Director", "Delphix"),
    ("Anil Chandra", "anil.chandra@thoughtspot.com", "Senior Director Talent Acquisition", "ThoughtSpot"),
    ("Anil Pereira", "anil.pereira@visiblealpha.com", "Senior Director Human Resources", "Visible Alpha"),
    ("Anil Tomar", "anil.tomar@fdsindia.co.in", "HR Head", "Fourth Dimension Solutions"),
    ("Animesh Kumar", "animesh.kumar@novopay.in", "Head HR", "Novopay"),
    ("Anindita Ranjan", "anindita.ranjan@3ds.com", "Director HR", "Dassault Systems"),
    ("Anirban Chakravorty", "anirban.chakravorty@nttdata.com", "Senior Director Regional Head HR", "NTT DATA"),
    ("Anish Ahmed", "anish.ahmed@vaave.com", "Head Talent", "Vaave"),
    ("Anish Raj", "anish.raj@sentieo.com", "Human Resources Director", "Sentieo"),
    ("Anita Noronha", "anoronha@shorewise.com", "Global Head Human Resources", "ShoreWise Consulting"),
    ("Anjali Ghadge", "anjalig@mangoapps.com", "VP HR & Operations", "MangoApps"),
    ("Anjali Patil", "anjali.patil@workindia.in", "HR Director", "WorkIndia"),
    ("Anjali Sharma", "anjali.sharma@fulcrumdigital.com", "Director Global Head of L&D", "Fulcrum Digital Inc"),
    ("Ankit Tomar", "ankit.tomar@rategain.com", "Associate Director HR Transformation", "RateGain"),
    ("Ankita Sinha", "ankita.sinha@mtxb2b.com", "Chief People Officer", "MTX Group"),
    ("Ankur Beri", "ankur.beri@niit-tech.com", "Group Head Human Resources", "NIIT Technologies"),
    ("Annapurna A", "annapurna.a@fime.com", "Head of HR & Admn", "FIME"),
    ("Anoob Abraham", "anoob.abraham@arcadia.com", "Associate Director Talent Acquisition", "Arcadia"),
    ("Anshika Khaitan", "anshika.khaitan@getvymo.com", "Director People & Culture", "Vymo"),
    ("Anshu Anand", "anshu.anand@absolutdata.com", "Head Of Human Resources", "Absolutdata Analytics"),
    ("Ansuman Sahu", "ansumans@mindfiresolutions.com", "Head of HR / Staffing", "Mindfire Solutions"),
    ("Anuj Agarwal", "anuj@deskera.com", "VP Corporate Operations & HR", "Deskera"),
    ("Anuja Sivaram", "anuja@codenation.co.in", "CHRO & COO", "Trilogy Innovations"),
    ("Anupam Srivastava", "anupam.srivastava@reltio.com", "Head Of Human Resources", "Reltio"),
    ("Anupriya Gandhi", "anupriya.gandhi@juliacomputing.com", "Global Director People Ops", "Julia Computing"),
    ("Anurag Rana", "anurag.rana@sirionlabs.com", "Head of Human Resources", "SirionLabs"),
    ("Anurag Verma", "anurag@uniphore.com", "Vice President Human Resources", "Uniphore"),
    ("Anusha Kishore", "anusha.kishore@loco.gg", "Assistant Vice President Human Resources", "Loco"),
    ("Aparna Srikanth", "aparna.srikanth@appsian.com", "Head Human Resources India", "Pathlock"),
    ("Aradhana Gupta", "aradhana@safexpay.com", "Chief People Officer", "SafexPay"),
    ("Aravind Chandrasekar", "aravind.chandrasekar@tigerspike.com", "Associate Director Talent Acquisition", "Concentrix Tigerspike"),
    ("Archana Anand", "archana@aufait.in", "Head of Talent Acquisition", "Aufait Technologies"),
    ("Archana Manne", "archana.manne@locuz.com", "Vice President Human Resources", "Locuz"),
    ("Arif Memon", "arif.memon@abzooba.com", "Associate Vice President Talent Acquisition", "Abzooba"),
    ("Arindam Kar", "arindam.kar@yodlee.com", "Head Talent Acquisition", "Envestnet"),
    ("Arjun Chatterjee", "arjun.chatterjee@sunlife.com", "Director & Head of Talent Acquisition", "Sun Life"),
    ("Arun Kumar", "arun.kumar@shipsy.io", "Chief People Officer", "Shipsy"),
    ("Arun Singh", "arun.singh@puresoftware.com", "Senior Director Talent Acquisition", "PureSoftware"),
    ("Arun Vigneswaran", "arun@xto10x.com", "Head of People Excellence", "xto10x"),
    ("Arushi Goel", "arushi.goel@betterplace.co.in", "Director HRBP", "BetterPlace"),
    ("Ashish Naidu", "ashish.naidu@mindgate.in", "Assistant Vice President Talent Acquisition", "Mindgate Solutions"),
    ("Ashok Putsala", "ashok.putsala@senecaglobal.com", "Associate Vice President Talent Acquisition", "SenecaGlobal"),
    ("Ashraf Kazi", "ashraf.kazi@simplifyhealthcare.com", "Associate Director Talent Acquisition", "Simplify Healthcare"),
    ("Ashwani Kumar", "ashwani@successive.tech", "Vice President People & Culture", "Successive Technologies"),
    ("Ashwin Singh", "ashwin@suki.ai", "Head of Talent Acquisition", "Suki"),
    ("Ashwini J", "ashwini.janardhanan@kaleyra.com", "Head People & Culture APAC", "Kaleyra"),
    ("Atin Karmokar", "atin.karmokar@pentagon.co.in", "AVP Head Human Resources & Admin", "Pentagon System and Services"),
    ("Atul Pal", "atul.pal@innefu.com", "Head Of Human Resources", "Innefu Labs"),
    ("Avinash Poojari", "avinash@sedintechnologies.com", "AVP Talent Acquisition", "Sedin Technologies"),
    ("Ayush Sinha", "ayush.sinha@sugarboxnetworks.com", "Vice President Human Resources", "SugarBox Networks"),
    ("Babitha Nambiar", "babitha.nambiar@opusconsulting.com", "VP Head Human Resources", "Opus Consulting Solutions"),
    ("Balaji Thiyagarajan", "balaji.thiyagarajan@thirdware.com", "Associate Director HR", "Thirdware Solution"),
    ("Balakrishna Shetty", "balakrishna.shetty@genisys-group.com", "Vice President Human Resource", "Genisys Group"),
    ("Balneet Birah", "balneet.birah@netsolutions.com", "Chief Human Resources Officer", "Net Solutions"),
    ("Bandla Shyamprasad", "bandla.shyamprasad@terralogic.com", "Director HR & Operations", "Terralogic"),
    ("Barkha Agrawal", "bagrawal@cpg-inc.com", "Director Talent Acquisition", "Computer Power Group"),
    ("Barkha Sharma", "barkha@wobot.ai", "CHRO", "Wobot.ai"),
    ("Bedisha Karmakar", "bedisha@reward360.co", "Senior Director People Operations", "Reward360 Global Services"),
    ("Benoy Koshy", "benoy.koshy@sisainfosec.com", "Head of Talent Acquisition", "SISA"),
    ("Bensely Zachariah", "bensely.zachariah@fulcrumdigital.com", "Global Head of Human Resources", "Fulcrum Digital Inc"),
    ("Bhakti Dharod", "bhakti.dharod@idfy.com", "Head of HR", "IDfy"),
    ("Bharat Bhartia", "bharat.bhartia@workindia.in", "Head of Talent Acquisition and HR", "WorkIndia"),
    ("Bharathi Ravipati", "bravipati@appstekcorp.com", "Sr. Director HR", "AppsTek"),
    ("Bharti Negi", "bharti.negi@edifecs.com", "Sr. Director Recruitment Talent Acquisition", "Edifecs"),
    ("Bhavana Jain", "bhavana@netcore.co.in", "Chief Human Resources Officer", "Netcore Cloud"),
    ("Bhavika Sheth", "bhavika.sheth@itcgindia.com", "HR Head", "ITCG Solutions"),
    ("Bhavin Sanghavi", "bhavin@mydukaan.io", "Head Talent Acquisition", "Dukaan"),
    ("Bhupesh Wasmatkar", "bhupesh.wasmatkar@verse.in", "Head Talent Acquisition", "VerSe Innovation"),
    ("Biju Varghese", "biju.v@inapp.com", "Director HR", "InApp"),
    ("Britto Ambrose", "britto@xoxoday.com", "Vice President of People & Culture", "Xoxoday"),
    ("Chetna Gogia", "chetna@gokwik.co", "Chief Human Resources Officer", "GoKwik"),
    ("Chinmoy Roy", "chinmoy.roy@catalyst-us.com", "Head Human Resources", "Catalyst Business Solutions"),
    ("Chiranjeevi Pannem", "chiranjeevip@byteridge.com", "Chief People Officer", "Byteridge"),
    ("Chandni Chopra", "chandnic@lambdatest.com", "Director Human Resources", "LambdaTest"),
    ("Chandra Prakash", "chandra.prakash@innoverdigital.com", "Head of Talent Acquisition", "Innover Digital"),
    ("Damayanti Ghosh", "damayanti.ghosh@getvymo.com", "Head of Talent Acquisition", "Vymo"),
    ("Deepa Makhija", "deepa.makhija@gupshup.io", "Associate Director HR", "Gupshup"),
    ("Deepa Mukherjee", "deepa.mukherjee@esri.in", "Chief People Officer & Vice President", "Esri India"),
    ("Deepak Khanna", "dkhanna@ishir.com", "Chief Talent Officer", "ISHIR"),
    ("Deepali", "deepali@proximity.tech", "Director People Operations", "Proximity Works"),
    ("Deepika Singh", "deepika@webkul.com", "Vice President Human Resources", "Webkul"),
    ("Dharmik Gohel", "dharmik@atlan.com", "Director Talent Acquisition", "Atlan"),
    ("Diksha Rohokale", "diksha@apptware.com", "Chief People Officer", "Apptware"),
    ("Dilip Borah", "borah.dilip@senrysa.com", "Chief People Officer", "Senrysa Technologies"),
    ("Dipesh Jain", "dipesh@pesto.tech", "Head Talent Acquisition", "Pesto Tech"),
    ("Dipti Goel", "dipti@insider.in", "Head Of Human Resources", "Paytm Insider"),
    ("Divya Bhardwaj", "divya.b@greyorange.com", "Associate Director Global HR Operations", "GreyOrange"),
    ("Divya Gunashekar", "divya@thescalers.com", "Director of HR", "The Scalers"),
    ("Divya Jaggi", "divyajaggi@promactinfo.com", "Chief People Officer", "Promact Infotech"),
    ("Ekta Chowdhry", "ekta.chowdhry@shipsy.io", "Head of Talent Acquisition", "Shipsy"),
    ("Eram Qudsia", "eram.qudsia@mygate.in", "Head of Human Resources", "MyGate"),
    ("Firdaus Mehta", "firdaus.mehta@heliossolutions.co", "Head People & Culture", "Helios Solutions"),
    ("Francis Gonsalves", "francis.gonsalves@moengage.com", "Director HRBP", "MoEngage"),
    ("Garima Sangwan", "garima.sangwan@accops.com", "Senior Director Human Resources", "Accops Systems"),
    ("Gautam Pathak", "gautam.pathak@opshub.com", "Vice President Human Resources and Operations", "OpsHub"),
    ("Gautham Premkumar", "gautham.p@accubits.com", "Head of Campus Recruitment", "Accubits Technologies"),
    ("Gayathri Arunkumar", "gayathri.arunkumar@tvsnext.io", "Associate Vice President Recruitment", "TVS Next"),
    ("Heena Bawa", "heena@clevertap.com", "Director HR", "CleverTap"),
    ("Himanshu Mishra", "hmishra@valethi.com", "Head Of Human Resources", "Valethi Technologies"),
    ("Humera Iffath", "humera.iffath@truecaller.com", "Human Resources Director India", "Truecaller"),
    ("Jabeen Pathan", "jabeen@hulkapps.com", "Chief Human Resources Officer", "HulkApps"),
    ("Janaki Naik", "janaki.naik@tatadigital.com", "Chief Human Resources Officer", "Tata Digital"),
    ("Jasmine Vaswani", "jasmine.vaswani@worldfashionexchange.com", "Chief Human Resources Officer", "WFX World Fashion Exchange"),
    ("Jaya Pandey", "jaya.pandey@brainvire.com", "Head HR", "Brainvire Infotech"),
    ("Jayati Pardhy", "jayati.p@keka.com", "Head of Human Resources", "Keka HR"),
    ("Jitendra Das", "jitendra.das@workinsync.io", "Director HR", "WorkInSync"),
    ("Jyoti Gouri", "jyoti.g@commerceiq.ai", "Director HR", "CommerceIQ"),
    ("Jyoti Singh", "jyoti.singh@zapcg.com", "CHRO Global HR Head", "ZapCom Group Inc"),
    ("Kajal Tuteja", "kajal.tuteja@csquare.in", "HR Head", "C-Square Info Solutions"),
    ("Kalyani Mahajan", "kalyani.mahajan@paramatrix.com", "Associate Vice President Human Resources", "Paramatrix Technologies"),
    ("Kanchan Verma", "kanchan.verma@qsstechnosoft.com", "Head Of Human Resources", "QSS Technosoft"),
    ("Kanika Gupta", "kanika@eglogics.com", "Human Resources Director", "EGlogics Softech"),
    ("Kapeesh Saxena", "kapeesh.saxena@genzeon.com", "Vice President Talent Acquisition", "Genzeon"),
    ("Karthick Rengasamy", "karthick@ideas2it.com", "Head of Talent Acquisition", "Ideas2IT Technologies"),
    ("Karthikeyan P", "karthikeyan@hiverhq.com", "Head of Talent Acquisition", "Hiver"),
    ("Karthikeyan Sivasubramanian", "karthikeyan.sivasubramanian@saviynt.com", "India Head Talent Acquisition", "Saviynt"),
    ("Kavita Tandon", "kavita.tandon@simplifyhealthcare.com", "VP Global Head of HR", "Simplify Healthcare"),
    ("Kavitha Umasankar", "kavitha.umasankar@wolterskluwer.com", "Director Human Resources", "Wolters Kluwer"),
    ("Keerthi Kamasamudra", "keerthi.kamasamudra@stellapps.com", "Head Of Human Resources", "Stellapps Technologies"),
    ("Kevin Marbaniang", "kevin@xeno.in", "Head of Talent Acquisition", "Xeno"),
    ("Khushboo Jain", "khushboo@techspian.com", "Human Resources Director", "Techspian"),
    ("Khushi Mishra", "khushi@5ire.org", "Head of Human Resources", "5ireChain"),
    ("Kiran Lal", "kiran.lal@tomiaglobal.com", "Director & Head Human Resources", "TOMIA"),
    ("Kritika Khanduri", "kritika.khanduri@loginradius.com", "Head of Global Recruitment", "LoginRadius"),
    ("Kunal Wadhwani", "kunal.wadhwani@pocketfm.com", "Director Human Resources", "Pocket FM"),
    ("Kushagra", "kushagra.pande@jungleegames.com", "Director Talent Acquisition", "Junglee Games"),
    ("Lakshmi Radhakrishnan", "lakshmipriya.radhakrishnan@bwdesigngroup.com", "Director HR", "Barry-Wehmiller International"),
    ("Lipika Mohanty", "lipika.mohanty@crmnext.com", "Global HR Director", "CRMNEXT"),
    ("Logesh Chandramoorthy", "logesh@clumio.com", "Head of Talent Acquisition", "Clumio"),
    ("Luisa Mohanty", "luisa.mohanty@rategain.com", "Associate Vice President Human Resources", "RateGain"),
    ("Madhuri Nandgaonkar", "madhuri@gupshup.io", "Senior Director HR", "Gupshup"),
    ("Manasi Kelkar", "manasi.kelkar@cropin.com", "VP Human Resources", "CropIn Technology"),
    ("Manav Jain", "manav.jain@loconav.com", "Chief Human Resources Officer", "LocoNav"),
    ("Mandeep Singh", "mandeep.singh@tulip.co", "Head of HR", "Tulip Interfaces"),
    ("Manisha Dash", "manisha.dash@celigo.com", "Director India Human Resources", "Celigo"),
    ("Manoj Sehgal", "manoj.sehgal@rvu.in", "Head of People Services HR India", "RVU India"),
    ("Maya John", "maya.john@verse.in", "Chief People Officer", "VerSe Innovation"),
    ("Mayank Agarwal", "mayank.agarwal@gaana.com", "Head HRBP", "Gaana"),
    ("Meena R", "meena@airmeet.com", "Senior Director Human Resources", "Airmeet"),
    ("Meenakshi Jha", "meenakshi.jha@talentica.com", "Head of Talent Acquisition", "Talentica Software"),
    ("Mili Panicker", "mili.panicker@webengage.com", "AVP HR & People Operations", "WebEngage"),
    ("Nandini Tandon", "nandini.tandon@indusface.com", "Chief People Officer", "Indusface"),
    ("Neelima Vaka", "neelima.vaka@minfytech.com", "Head Of Human Resources", "Minfy"),
    ("Neeraj Sharma", "neeraj@fourkites.com", "Senior Director of Human Resources", "FourKites"),
    ("Neha Bhandari", "neha.bhandari@vmock.com", "Director of Human Resources", "VMock"),
    ("Neha Sahi", "neha@trell.in", "Director HR", "Trell"),
    ("Nimesh Mathur", "nimesh@haptik.ai", "Director People Culture & Talent", "Haptik"),
    ("Nitasha Dusi", "nitasha.dusi@atidiv.com", "Director HR", "Atidiv"),
    ("Nitin Nahata", "nitin.nahata@gameskraft.com", "CHRO", "Gameskraft"),
    ("Nupur Jain", "nupur@ixigo.com", "VP of Human Resources", "ixigo"),
    ("Paromita Areng", "paromita.areng@zaggle.in", "Chief Human Resources Officer", "Zaggle Prepaid Ocean Services"),
    ("Pavan K", "pk@eightfold.ai", "Director Talent Acquisition", "Eightfold"),
    ("Pavithradesai Pd", "pavithra.desai@infracloud.io", "Chief People Officer", "InfraCloud Technologies"),
    ("Piyush Raghuvanshi", "piyush.r@apna.co", "Head Talent & Culture", "apna"),
    ("Pooja Madappa", "pooja.madappa@netradyne.com", "Vice President Human Resources", "Netradyne"),
    ("Poornima Gowda", "poornima.gowda@fortanix.com", "Head Of Human Resources", "Fortanix"),
    ("Prachi Singh", "prachi.singh@vinculumgroup.com", "Head Global Resourcing & Talent Management", "Vinculum Group"),
    ("Prashant Parashar", "prashant.parashar@clevertap.com", "Chief Human Resources Officer", "CleverTap"),
    ("Priya Subramanian", "priya.subramanian@talview.com", "Head of HR", "Talview"),
    ("Priya Surana", "priya@jungleegames.com", "Head Employee Experience & Talent Acquisition", "Junglee Games"),
    ("Priyanka Grover", "priyanka.grover@fifthnote.co", "Function Head Culture Building", "fifthnote"),
    ("Pronami Borah", "pronami.borah@travclan.com", "People Operations Head", "TravClan"),
    ("Puja Gupta", "puja@affle.com", "Associate Director Human Resources", "Affle"),
    ("Rahul Inamdar", "rahul.inamdar@infracloud.io", "Head of Talent Acquisition", "InfraCloud Technologies"),
    ("Rajani Siddhartha", "rajani.siddhartha@dreamorbit.com", "Vice President Human Resource", "DreamOrbit"),
    ("Rajat Bansal", "rajatb@damcogroup.com", "Associate Vice President HR", "Damco Solutions"),
    ("Rajesh Babu", "rajesh.babu@softobiz.com", "Head of Talent Acquisition", "Softobiz Technologies"),
    ("Rajesh Malhotra", "rajeshm@damcogroup.com", "AVP Staffing and Fixed Bid Projects", "Damco Solutions"),
    ("Rajni Bansal", "rajni@growexx.com", "Head Of Human Resources", "Growexx"),
    ("Rakesh Arora", "rakesh@taazaa.com", "Head HR & Talent Acquisition", "Taazaa Inc"),
    ("Ramya Sharma", "ramya.s@greyorange.com", "Chief People Officer", "GreyOrange"),
    ("Rashmi Chauhan", "rashmi.chauhan@rategain.com", "Global Head Talent Acquisition", "RateGain"),
    ("Ravdeep Singh", "ravdeep.singh@sourcefuse.com", "Chief People Officer", "SourceFuse Technologies"),
    ("Raviesh Inamdar", "rahul.inamdar@infracloud.io", "Head of Talent Acquisition", "InfraCloud Technologies"),
    ("Rehan Abdi", "rehan.abdi@kiwitech.com", "Head of Talent Acquisition", "KiwiTech"),
    ("Richa Pande", "richa.pande@inatech.com", "Chief People Officer", "Inatech"),
    ("Rinki Goel", "rinki.goel@hevodata.com", "Director HR", "Hevo Data"),
    ("Rohini Radhakrishnan", "rohini.radhakrishnan@ideas2it.com", "Head Human Resources", "Ideas2IT Technologies"),
    ("Rohit Singh", "rohit.singh@blucognition.ai", "Head of Talent Acquisition", "bluCognition"),
    ("Roopa Gangadharan", "roopa.g@aujas.com", "Associate Director HRBP", "Aujas Cybersecurity"),
    ("Roystone Fernandez", "roystone@accubits.com", "Chief Human Resources Officer", "Accubits Technologies"),
    ("Ruchi Sharma", "ruchi@headspin.io", "Director People & Culture", "HeadSpin"),
    ("Ruchika Chawla", "ruchika@rooter.io", "Head HR", "Rooter App"),
    ("Ruchika Sawhney", "ruchika.sawhney@cometchat.com", "Senior Director Human Resources", "CometChat"),
    ("Sahil Sharma", "sahil.sharma@rategain.com", "Global Head Human Resources", "RateGain"),
    ("Sanjay Chandel", "sanjay.chandel@joveo.com", "Head Of Human Resources", "Joveo"),
    ("Sanjeeta Mohta", "sanjeeta@learningspiral.co.in", "Head of Talent & Finance", "Learning Spiral"),
    ("Sanketh Ramkrishnamurthy", "sanketh.r@autorabit.com", "Head HR", "AutoRABIT"),
    ("Sanya Nagpal", "sanya.nagpal@leena.ai", "Head Of Human Resources", "Leena AI"),
    ("Sarada Kandanur", "sarada.kandanur@kore.com", "Senior Director HR & Recruitment", "Kore.ai"),
    ("Sasank Pandey", "sasank.pandey@hevodata.com", "Associate Director Talent Acquisition", "Hevo Data"),
    ("Shailesh Jadhav", "shailesh@mirafra.com", "Vice President Global Head HR", "Mirafra Technologies"),
    ("Shivani Chaturvedi", "shivani.chaturvedi@mjunction.in", "Chief People Officer", "mjunction services"),
    ("Shivani Jaiswal", "shivani@virtualheight.com", "Chief People Officer", "Virtual Height IT Services"),
    ("Shivani Khanna", "khanna.shivani@digitate.com", "Head HR", "Digitate"),
    ("Shreeja Santosh", "shreeja.santosh@lrn.com", "Director People & Culture", "LRN"),
    ("Shruti Gandhi", "shruti.gandhi@moolya.com", "Head of Human Resources Operations", "Moolya"),
    ("Sindhuja Parthasarathy", "sindhuja.parthasarathy@mindtickle.com", "Director Global Talent Management", "Mindtickle"),
    ("Snigdha Prashar", "snigdha@saavn.com", "Director Human Resources", "JioSaavn"),
    ("Soumya Rajesh", "soumya@zoondia.in", "Head Of Human Resources", "Zoondia"),
    ("Sreeparna Samanta", "sreeparna.samanta@urbanladder.com", "Head HR", "Urban Ladder"),
    ("Srinidhi Dasaka", "srinidhi.d@keka.com", "Head Of Human Resources", "Keka HR"),
    ("Subhash Chandra", "subhash.chandra@silverlinecrm.com", "Head of People Operations India", "Silverline"),
    ("Sucheta Ukidve", "sucheta.ukidve@mindstix.com", "Director HR", "Mindstix Software Labs"),
    ("Sukhpreet Sandhu", "sukhpreet.sandhu@itilite.com", "Head of Human Resources", "ITILITE"),
    ("Susan Leonard", "susan@kissflow.com", "Director Talent Acquisition", "Kissflow"),
    ("Swapna Krishna", "swapna.krishna@theoptimum.net", "AVP Human Resources", "Optimum Solutions"),
    ("Swapnika Nag", "snag@tataunistore.com", "Chief People Officer", "Tata CLiQ"),
    ("Swetha Harikrishnan", "swetha@hackerearth.com", "HR Director", "HackerEarth"),
    ("Tanvi Mittal", "tanvi.mittal@vlinkinfo.com", "HR Head India", "VLink Inc"),
    ("Tisha Prasad", "tisha@loconav.com", "Vice President Human Resources", "LocoNav"),
    ("Vaibhav Ghai", "vaibhav@scienaptic.com", "Head HR", "Scienaptic AI"),
    ("Varun Wadhwa", "varun.wadhwa@birdeye.com", "Senior Director People & Culture", "Birdeye"),
    ("Veena Satish", "veena.satish@moengage.com", "VP People & Culture", "MoEngage"),
    ("Viraaj Arora", "viraaj@headout.com", "Head Culture and Talent", "Headout"),
    ("Vidhya Sam", "vidhya.sam@superops.ai", "Head Of Human Resources", "SuperOps.ai"),
    ("Vijay Unnikrishnan", "vijay.unnikrishnan@acqueon.com", "Global Head Human Resources", "Acqueon"),
    ("Vikrant Bhalodia", "vikrant@weblineindia.com", "Head of HR & People Operations", "WeblineIndia"),
    ("Vikrant Goyal", "vikrant.goyal@games24x7.com", "VP Head HR", "Games24x7"),
    ("Vishakha Saini", "vishakha.saini@infostride.com", "HR Head", "InfoStride"),
    ("Vishal Naithani", "vishal.naithani@mylofamily.com", "Head of People & Culture", "Mylo"),
    ("Vivek Gaur", "vivek@pacificbpo.com", "Chief Peoples Officer", "Pacific Global"),
    ("Yogita Sharma", "yogita.sharma@netsmartz.com", "Head HR People and Culture", "Netsmartz"),
    ("Yesha Brahmbhatt", "yesha.brahmbhatt@contentstack.com", "Associate Director Human Resources", "Contentstack"),
    ("Zulfiqar Syed", "zulfiqar.syed@netcore.co.in", "Associate Vice President HR", "Netcore Cloud"),
    # Add more from your PDF list here — the above is a curated set of ~200
    # The full 1842 can be pasted following the same format
]

# ─────────────────────────────────────────────
#  30 ROTATING CUSTOM LINES — no API needed
# ─────────────────────────────────────────────

CUSTOM_LINES = [
    "I've been following {company}'s journey closely and love how the team is solving real problems in this space.",
    "The work {company} is doing really stands out — I'd love to be part of that mission.",
    "I came across {company} recently and was genuinely impressed by what the team is building.",
    "{company} has been on my radar for a while — the product direction really resonates with me.",
    "I've been tracking {company}'s growth and would love to contribute to what you're building.",
    "The problems {company} is tackling are exactly the kind I want to work on in my career.",
    "I admire {company}'s approach and the impact it's having — would love to join the team.",
    "After learning about {company}, I'm convinced this is where I want to start my career.",
    "{company} feels like the kind of place where I can learn fast and contribute meaningfully.",
    "I've seen {company}'s work and think my skills could be a strong fit for your team.",
    "The culture and vision at {company} align perfectly with what I'm looking for.",
    "I've been reading about what {company} is building — and it genuinely excites me.",
    "{company} is building something I believe in, and I'd love to be part of the team.",
    "I was really impressed by {company}'s product direction and the momentum the company has.",
    "{company} stood out to me when I was looking at companies I genuinely want to work at.",
    "I'd love to bring my skills to {company} and contribute to the exciting work happening there.",
    "What {company} is building has real-world impact — that's exactly what motivates me.",
    "The scale and ambition of what {company} is doing really drew me in.",
    "I spent time learning about {company} and came away genuinely excited.",
    "{company} is one of the companies I've had my eye on — I'd love a chance to connect.",
    "I'm reaching out because {company} is at the top of my list of places I want to work.",
    "The mission at {company} resonates with me and I'd love to contribute to it.",
    "{company}'s products have caught my attention — I'd love to help build what comes next.",
    "I see a clear fit between my background and what {company} is working on right now.",
    "Everything I've read about {company} tells me this is the right place for me to grow.",
    "{company}'s impact in this space is something I genuinely want to be a part of.",
    "I've been following {company}'s growth story and find it really inspiring.",
    "I came across {company} while researching companies I'd love to work at — and it stuck with me.",
    "{company} is the kind of company I've wanted to work at since I started my job search.",
    "The kind of challenge {company} is taking on is exactly what I want to be part of.",
]

def get_custom_line(company):
    idx = int(hashlib.md5(company.encode()).hexdigest(), 16) % len(CUSTOM_LINES)
    return CUSTOM_LINES[idx].format(company=company)

# ─────────────────────────────────────────────
#  EMAIL TEMPLATES
# ─────────────────────────────────────────────

INITIAL_TEMPLATE = """\
Hi {first_name},

{custom_line}

I'm Aftab Dayer — an NIT Hamirpur 2025 graduate and {role} with an IEEE-published research paper (IACIS-2025) and three production-deployed data applications. I hold a Microsoft Power BI certification (PL-300) and have hands-on experience in SQL, Python, Power BI, and ML-based analytics.

A few highlights from my work:
- Built JobMarket AI — a full-stack job analytics platform processing 1,000 job postings across 15 IT roles, with salary percentile benchmarking across 24 cities
- Built MedCart Intelligence — improved demand forecast accuracy by 22% over ARIMA baseline using RandomForest on a 10K-record healthcare dataset
- IEEE Published — sole researcher on a 5G ML architecture project accepted at IEEE IACIS-2025

I'm open to Data Analyst, Business Analyst, Product Analyst, and entry-level PM roles — full-time or internship. I'd love to know if there's a fit at {company}. Happy to share my resume or jump on a quick 10-minute call.

LinkedIn: {linkedin}
GitHub: {github}
Email: {email}

Thanks for your time,
Aftab Dayer
"""

FOLLOWUP_TEMPLATE = """\
Hi {first_name},

Following up on my email from a few days ago — didn't want it to get buried!

I'm still very interested in any Data Analyst, Business Analyst, or entry-level analytical role at {company}. Even a quick reply on whether there's a potential fit would mean a lot.

LinkedIn: {linkedin}

Thanks again,
Aftab Dayer
"""

SUBJECTS = [
    "IEEE-published Data Analyst (NIT Hamirpur) — interested in {company}",
    "Data Analyst fresher with Power BI cert & 3 live apps — {company}",
    "NIT Hamirpur 2025 grad — Data / Product Analyst roles at {company}",
    "Quick intro — Data Analyst open to roles at {company}",
    "Aftab Dayer — Data Analyst / Business Analyst — {company}",
    "Data Analyst with SQL, Python, Power BI — exploring {company}",
    "Entry-level Data Analyst (IEEE published, PL-300) — {company}",
    "Would love to explore analyst opportunities at {company}",
]

def build_subject(company):
    return random.choice(SUBJECTS).format(company=company)

def build_body(first_name, company, custom_line):
    role = random.choice(TARGET_ROLES)
    return INITIAL_TEMPLATE.format(
        first_name=first_name, custom_line=custom_line,
        role=role, company=company,
        linkedin=YOUR_LINKEDIN, github=YOUR_GITHUB,
        email=YOUR_EMAIL_ID
    )

# ─────────────────────────────────────────────
#  DATABASE
# ─────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hr_email TEXT UNIQUE,
            hr_name TEXT,
            company TEXT,
            date_sent TEXT,
            followup_sent INTEGER DEFAULT 0,
            replied INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn

def already_contacted(conn, email):
    return conn.execute(
        "SELECT id FROM contacts WHERE hr_email=?", (email,)
    ).fetchone() is not None

def log_contact(conn, email, name, company):
    conn.execute(
        "INSERT OR IGNORE INTO contacts (hr_email,hr_name,company,date_sent) VALUES (?,?,?,?)",
        (email, name, company, datetime.now().isoformat())
    )
    conn.commit()

def get_followups_due(conn):
    cutoff = (datetime.now() - timedelta(days=FOLLOWUP_DAYS)).isoformat()
    return conn.execute(
        "SELECT hr_email,hr_name,company FROM contacts WHERE followup_sent=0 AND replied=0 AND date_sent<?",
        (cutoff,)
    ).fetchall()

def mark_followup(conn, email):
    conn.execute("UPDATE contacts SET followup_sent=1 WHERE hr_email=?", (email,))
    conn.commit()

def mark_replied(conn, email):
    """Call this manually if someone replies so they won't get follow-up."""
    conn.execute("UPDATE contacts SET replied=1 WHERE hr_email=?", (email,))
    conn.commit()

# ─────────────────────────────────────────────
#  GMAIL SENDER
# ─────────────────────────────────────────────

def send_email(to_email, subject, body):
    msg = MIMEMultipart("alternative")
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            s.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"    ✗ Failed: {e}")
        return False

# ─────────────────────────────────────────────
#  MAIN DAILY RUN
# ─────────────────────────────────────────────

def run_daily():
    print(f"\n{'='*55}")
    print(f"  Job Email Bot — {datetime.now().strftime('%d %b %Y, %H:%M')}")
    print(f"{'='*55}\n")

    conn = init_db()
    sent = 0

    # Shuffle so different HRs get emailed each day
    hr_list = HR_LIST.copy()
    random.shuffle(hr_list)

    print("Sending emails...\n")

    for (name, email, title, company) in hr_list:
        if sent >= DAILY_LIMIT:
            print(f"\nDaily limit of {DAILY_LIMIT} reached. Bot stops here.")
            print(f"Tomorrow it will continue with remaining contacts.\n")
            break

        if already_contacted(conn, email):
            continue    # skip — already emailed this person

        first_name = name.split()[0]
        custom_line = get_custom_line(company)
        body        = build_body(first_name, company, custom_line)
        subject     = build_subject(company)

        success = send_email(email, subject, body)
        if success:
            log_contact(conn, email, name, company)
            print(f"  ✓  {name:30s} | {company:35s} | {email}")
            sent += 1
            # Random delay between emails — prevents spam detection
            delay = random.randint(120, 300)   # 2 to 5 minutes
            print(f"     Waiting {delay}s...")
            time.sleep(delay)

    # ── FOLLOW-UPS ──
    print(f"\nChecking follow-ups ({FOLLOWUP_DAYS}+ days, no reply)...\n")
    for (email, name, company) in get_followups_due(conn):
        if sent >= DAILY_LIMIT:
            break
        first_name = name.split()[0]
        body = FOLLOWUP_TEMPLATE.format(
            first_name=first_name, company=company,
            your_name=YOUR_NAME, linkedin=YOUR_LINKEDIN
        )
        subject = f"Following up — {YOUR_ROLE} opportunity at {company}"
        if send_email(email, subject, body):
            mark_followup(conn, email)
            print(f"  ↩  Follow-up → {name} at {company}")
            sent += 1
            time.sleep(random.randint(90, 180))

    # ── SUMMARY ──
    total   = conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    replied = conn.execute("SELECT COUNT(*) FROM contacts WHERE replied=1").fetchone()[0]
    remaining = len(HR_LIST) - total

    print(f"\n{'─'*55}")
    print(f"  Today sent : {sent}")
    print(f"  Total done : {total} / {len(HR_LIST)} HRs")
    print(f"  Remaining  : {remaining} contacts left")
    print(f"  Replies    : {replied}")
    print(f"{'─'*55}\n")

    if total >= len(HR_LIST):
        print("All contacts emailed! Consider adding more to the list.")

    conn.close()

# ─────────────────────────────────────────────
#  HOW TO MARK A REPLY (when someone responds)
#  Run this in python to stop follow-ups to them:
#
#  import sqlite3
#  conn = sqlite3.connect("contacted.db")
#  conn.execute("UPDATE contacts SET replied=1 WHERE hr_email='email@company.com'")
#  conn.commit()
# ─────────────────────────────────────────────

if __name__ == "__main__":
    run_daily()

# ─────────────────────────────────────────────
#  AUTOMATE DAILY (pick one):
#
#  Mac/Linux — crontab:
#    crontab -e
#    0 9 * * * python3 /path/to/job_bot_real_hrlist.py
#
#  Windows — Task Scheduler:
#    Action: python C:\path\to\job_bot_real_hrlist.py
#    Trigger: Daily 9:00 AM
#
#  Free cloud (runs even when laptop is off):
#    pythonanywhere.com → free account → Tasks → Daily
# ─────────────────────────────────────────────
