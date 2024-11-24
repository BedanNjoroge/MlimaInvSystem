# Project Overview

This project is designed for a client in the granite mining industry, with the goal of building an inventory management system that accurately tracks inventory movement through each stage of production. The inventory process begins at the quarry, where raw granite is mined and cut into boulders. Both quality boulders and rejects (boulders that do not meet quality standards) are recorded in the system. Quality boulders proceed to the factory, while rejects are logged and set aside.

Within the factory, production moves through multiple stages, starting with the Cutting Section, which is equipped with two cutting machines. These machines slice boulders into slabs, and at each stage—Cutting, Separation, Polishing, Edge Cutting, Bullnose, and Sealant Application—both quality and reject slabs are recorded. Reject slabs, which may arise due to issues like incorrect thickness, cracks, or breakage, are also tracked in the system.

The stages in the production process are as follows:

1. Cutting: Boulders are sliced into slabs, generating both quality and reject slabs.
2. Separation: Slabs are separated from any remaining boulder pieces and sent to the polishing stage.
3. Polishing: Slabs undergo surface smoothening for quality finishing.
4. Edge Cutting: Slabs are cut to a standard size (2400x600mm) with options for special order sizes as required by clients.
5. Bullnose: One side of the slabs is curved to give a rounded edge.
6. Sealant Application: Slabs are treated with a sealant for waterproofing, making them ready for sale.

Once all stages are complete, slabs are dispatched to the warehouse for storage and are eventually sold from there. The system will maintain real-time inventory balances across all production stages, from quarry to warehouse, tracking stock movement at each step. Sales from the warehouse will reduce the inventory balance accordingly.

In addition to tracking slabs and boulders, the system will manage essential factory and quarry inventory, including spare parts, consumables, operational equipment, lubricants, and construction materials. Worn-out machine parts, which may or may not be reusable, will also be recorded to ensure efficient use of resources and maintenance.

**Automated Reporting with Slack Notifications**

To streamline monitoring and reporting, the system will automate end-of-day reports using Slack notifications. These notifications will include:

1. The number of boulders mined each day.
2. The total number of slabs ready for dispatch at the end of each day.
3. A summary of slabs dispatched to the warehouse.
4. A report of slabs issued from the warehouse for sales.
5. The remaining slab inventory balance in the warehouse.
6. Month to date usage of consumables.

This feature will streamline communication and provide real-time visibility into daily inventory statuses.

**Technology Stack**

1. Programming Language: Python
2. Database: SQLite for structured storage of inventory data.
3. Framework: Flask for building a user-friendly web application.
4. Frontend: HTML/CSS for the web interface.
5. Automation: Slack API for sending daily inventory reports and updates.
6. Deployment Platform: Heroku for deploying and hosting the web application, making it easily accessible to the client and their team.

By deploying on Heroku, this application will be accessible online, allowing stakeholders to monitor and manage inventory in real-time, from any device with internet access. Heroku’s reliable hosting infrastructure ensures that the system remains scalable and responsive as inventory needs grow.

This project will offer a comprehensive inventory management solution, providing real-time tracking, insightful reports, and remote accessibility for streamlined granite production and inventory control.

The folder structure is as below:

```bash
mlima_granite_inventory_system/
│
├── app.py                   # Main Flask application file
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
├── Procfile                 # Heroku process file
├── runtime.txt              # Python runtime version
│
├── templates/               # HTML templates for Flask
│   ├── index.html
│   ├── quarry.html
│   ├── factory.html
│   ├── separation.html
│   ├── polishing.html
│   ├── edge_cutting.html
│   ├── edge_polishing.html
│   ├── sealant.html
│   ├── warehouse.html
│   └── requisition.html
│
├── static/                  # Static files (CSS, JS, images)
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
├── database/                # Directory for SQLite database file
│   └── inventory.db
│
└── logs/                    # Directory for log files
    └── app.log
```