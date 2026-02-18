Subject: Pecan POS Project Plan (Python + Azure) and What I Need From You

Hi Joshua,

Thanks again for collaborating on the GitHub repo.

I’ve prepared the project plan for a simple Python desktop POS app (Windows .exe) with Azure SQL as the primary database, and a legacy Microsoft Access migration path.

### Software design (simple MVP)
- **Desktop app:** Python (PySide6) running locally on your Windows PC.
- **Database:** Azure SQL Database for customers, products, sales, and receipt metadata.
- **Receipts:** PDF generated locally and saved on your machine (with optional Azure archive later).
- **Payments:** We will record payment type (Cash/Card/Other) only—no payment processor integration in MVP.
- **Legacy system:** Your Access database will be treated as the current source during migration, then validated before cutover.

### What I need from you (Azure + legacy)
1. **Azure subscription access** (or someone on your team who can provision resources).
2. **Azure SQL details** once created:
   - Server name (e.g., `yourserver.database.windows.net`)
   - Database name
   - App username/password (least privilege account)
3. **Firewall/IP allow-list info** for the business PC(s) that will run the app.
4. **Legacy Access files** (`.accdb`/`.mdb`) and any notes about table meanings.
5. **Business receipt details**:
   - Business name/address/phone
   - Return policy/thank-you text

### Local deployment plan
- I’ll package the app as a **Windows .exe** via PyInstaller.
- You’ll run an installer on the target PC.
- On first launch, we’ll enter Azure SQL connection settings and test connection.
- Daily use is simple: manage products/customers, ring up sales, and print/save receipts.

### GitHub Issues
I also added a structured issue backlog for tracking delivery step-by-step, including discovery, Azure setup, migration, POS, receipts, reporting, packaging, and QA.

If you send Azure/database access details, I can start implementation immediately.

Thanks,
[Your Name]
