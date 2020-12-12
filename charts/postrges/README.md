```
helm install postgres bitnami/postgresql -f values.yaml --create-namespace -n postgres
```

```
helm delete postgres -n postgres
```

```
kubectl delete pvc -l release=postgres -n postgres
kubectl delete ns postgres
```
