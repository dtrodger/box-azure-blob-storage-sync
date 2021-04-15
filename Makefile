help:
	@echo
	@echo
	@echo "  -----------------------------------------------------------------------------------------------------------"
	@echo "  State of Florida Box Platform app Makefile"
	@echo "  -----------------------------------------------------------------------------------------------------------"
	@echo "  dev"
	@echo "  prod"
	@echo
	@echo

dev:
	docker-compose -f docker-compose.dev.yml up --build

prod:
	docker-compose up --build