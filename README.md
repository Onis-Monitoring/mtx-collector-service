# mtx-collector-service
Flask Service Matrixx Collector

# Manual Start
1.-
	Tul
	kubectl cp . matrixx-prod-int/backup-5b9f79cc5-jcdzd:/home/mtx/gunicorn
	
2.-
	kubectl exec -it backup-5b9f79cc5-jcdzd -n matrixx-prod-int bash
	
3.-
	ssh -i /etc/mef-publishing-ssh-secret/ssh-privatekey mtxdepmef@10.237.30.88
		[Optional] yes
		exit
	
4.-
	print_event_repository_loader_trace.py -g --host=10.237.3.143
		MtxAdmin
		NMBYmN9J
		y

5.-
	cd home/mtx/gunicorn
	nohup gunicorn -w 12 -b :5000 'app.main:create_app()' --timeout 90 &
		enter
	cat nohup.out 
	rm nohup.out

6.-
	Spr
	kubectl cp . matrixx-prod-int/backup-7d9cc5668c-hqxwb:/home/mtx/gunicorn

7.-
	kubectl exec -it backup-7d9cc5668c-hqxwb -n matrixx-prod-int bash
	Repeat 3,4,5

# Stop service
pkill gunicorn

# docker
docker build -t mtx_collector_test .
docker run -it --name mtx_collector -p 5000:5000 mtx_collector_test

# docker compose
docker-compose up [mtx-exporter]
docker-compose stop mtx-exporter

# k8s
kubectl create ns [NS_NAME]
kubectl apply -f Deployment.yaml