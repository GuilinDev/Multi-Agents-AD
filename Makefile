.PHONY: api mobile dev

api:
	cd api && uvicorn main:app --host 0.0.0.0 --port 8000 --reload

mobile:
	cd mobile && npx expo start

dev:
	$(MAKE) api & $(MAKE) mobile
