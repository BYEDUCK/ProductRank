export GOOGLE_APPLICATION_CREDENTIALS=$GAC
gcloud functions deploy product-rank \
--region=europe-central2 \
--runtime=python310 \
--entry-point=main \
--memory=128MB \
--trigger-http