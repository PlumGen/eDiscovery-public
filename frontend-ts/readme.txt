to start locally
frontend
conda activate eDiscovery
cd appfolder
npm run start


backend
conda activate ediscovery
cd dataprep
$env:FLASK_APP = "mainfaiss:app"
flask run --host=0.0.0.0 --port=5000
