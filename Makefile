.PHONY: api mobile web dev

api:
	cd api && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

mobile:
	cd mobile && npx expo start

web:
	cd web && npm run dev

dev:
	$(MAKE) api & $(MAKE) mobile & $(MAKE) web
