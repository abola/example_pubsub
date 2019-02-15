# Google Pub/Sub Example

請點以下圖示，開啟您的 Google cloud shell
<a href="https://console.cloud.google.com/cloudshell/editor?shellonly=true" target="_blank"><img src="https://gstatic.com/cloudssh/images/open-btn.png" alt="在 Cloud Shell 中開啟"/></a>


## 前置作業

請先確認以下項目，以確保後續的動作順利進行

## 取得原始碼 

你可以直接[下載原始碼]或使用 git

### 使用 git 下載原始碼 

```bash
git clone some where
```

### 進入專案目錄

```bash
cd examples_pubsub
```

### 在 cloud shell 中開啟本教程 (optional)

```bash 
cloudshell launch-tutorial README.md
```

## 設定環境變數

你會在本頁中，設定後續動作所需的環境變數

### 產生亂數序號

亂數產生一組序號，防止範例執行過程中出現衝突

```bash
export RND_KEY=$(cat \
    /proc/sys/kernel/random/uuid | \
    awk -F"-" '{print $5}')
```

### 設定各項環境變數名稱

執行以下指令，會設定本教程中，所有使用到的環境變數

```bash
export $(envsubst < environments | grep -v '^#' | xargs)
```

詳細的內容，您可以參考檔案[environments]或以下內容

```
# frontend image 名稱
FRONTEND_IMAGE=frontend-image-${RND_KEY}
# backend image 名稱
BACKEND_IMAGE=backend-image-${RND_KEY}
# 示範用專案ID 
GCP_PROJECT_ID=pubsub-projectid-${RND_KEY}
# 偏好的 GCP zone
GCP_ZONE=asia-east1-a
# GKE 名稱 
GCP_GKE_NAME=pubsub-k8s-name-${RND_KEY}
# Google Pub/Sub admin Service Account
GCP_PUBSUB_ADMIN=pubsub-admin-${RND_KEY}
# Google Pub/Sub request name
GCP_PUBSUB_REQUEST_NAME=pubsub-request-${RND_KEY}
# Google Pub/Sub response name
GCP_PUBSUB_RESPONSE_NAME=pubsub-response-${RND_KEY}
```

## 建立 GCP 專案與服務

### 建立專案

```bash
gcloud projects create ${GCP_PROJECT_ID}
```

```bash
gcloud config set project ${GCP_PROJECT_ID}
```

## 建你的新專案連接計費帳戶

在進行下一步之前，您必需為您新建的專案設定計費帳戶才能進行

### 取得網址，並在網頁中開啟設定

```bash
echo "https://console.developers.google.com/project/${GCP_PROJECT_ID}/settings"
```

## 建立 kubernetes 服務

### 開啟 kubernetes API 使用權限

這指令會啟用您帳號調用 kubernetes API 的權限，過程約需等待 2分鐘

```bash
gcloud services enable container.googleapis.com
```

### 開始建立 k8s 叢集

建立 k8s 叢集, 過程約需等待 3分鐘

```bash
gcloud container clusters create \
  ${GCP_GKE_NAME} \
  --cluster-version=1.11.6-gke.2 \
  --zone ${GCP_ZONE} \
  --project ${GCP_PROJECT_ID}  \
  --machine-type "custom-2-8192" \
  --num-nodes "1"
```

### 取得k8s憑證

透過 gcloud 指令輔助，取回 k8s 憑證，並設置於 kubectl

```bash
gcloud container clusters get-credentials \
  ${GCP_GKE_NAME} \
  --zone ${GCP_ZONE} \
  --project ${GCP_PROJECT_ID} 
```


## 建立 pubsub 發佈與訂閱項目

### 建立 request/response 兩組 topic

```bash
gcloud pubsub topics create ${GCP_PUBSUB_REQUEST_NAME}
```

```bash
gcloud pubsub topics create ${GCP_PUBSUB_RESPONSE_NAME}
```

> 我們不用在此建立訂閱，訂閱由使用方(軟體)自行建立較合適

## 建立操作 pubsub 服務帳戶

### 建立一組新的服務帳戶

```bash
gcloud iam service-accounts create ${GCP_PUBSUB_ADMIN}
```
 
### 指定 roles/pubsub.admin 權限給予帳戶

```bash
gcloud projects add-iam-policy-binding \
  ${GCP_PROJECT_ID} \
  --member serviceAccount:${GCP_PUBSUB_ADMIN}@${GCP_PROJECT_ID}.iam.gserviceaccount.com \
  --role roles/pubsub.admin
```

### 取回認證檔

```bash
gcloud iam service-accounts keys create \
  ${GCP_PUBSUB_ADMIN}.json \
  --iam-account=${GCP_PUBSUB_ADMIN}@${GCP_PROJECT_ID}.iam.gserviceaccount.com
```

## 產生 frontend image

本步驟會將 frontend 端的程式，打包成 docker image 並上傳至 GCR

### 拷貝憑證資料

```bash
cp ${GCP_PUBSUB_ADMIN}.json ./frontend/pubsub.json
```

### 建立 frontend image & push

```bash
cd frontend \
&& docker build \
  -t gcr.io/${GCP_PROJECT_ID}/${FRONTEND_IMAGE} \
  . \
&& docker push gcr.io/${GCP_PROJECT_ID}/${FRONTEND_IMAGE} \
&& cd ..
```


## 產生 backend image

本步驟會將 backend 端的程式，打包成 docker image 並上傳至 GCR

### 拷貝憑證資料

```bash
cp ${GCP_PUBSUB_ADMIN}.json ./backend/pubsub.json
```

### 建立 backend image & push

```bash
cd backend \
&& docker build \
  -t gcr.io/${GCP_PROJECT_ID}/${BACKEND_IMAGE} \
  . \
&& docker push gcr.io/${GCP_PROJECT_ID}/${BACKEND_IMAGE} \
&& cd ..
```

## 配置 yaml 設定，將服務啟動於 GKE

### 設定 credential file path

```bash
# Google pub/sub credential file path
GOOGLE_APPLICATION_CREDENTIALS=/etc/google/auth/pubsub.json
```

### 啟動 frontend/backend/redis 服務

```bash
envsubst < deploy.yaml | kubectl apply -f -
```

### 等待服務 ip 配發 

```bash
watch -n1 kubectl get svc
```

## 完成

最後請記得，刪除本次練習的專案，以節省費用

```bash
gcloud projects delete ${GCP_PROJECT_ID}
```

[cloud shell]: (https://console.cloud.google.com/cloudshell/editor?shellonly=true)
[environments]: (./environments)
[下載原始碼]: (http://www.google.com)