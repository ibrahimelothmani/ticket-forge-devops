package com.ticketforge.apigateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ApigatewayApplication {

	public static void main(String[] args) {
		SpringApplication.run(ApigatewayApplication.class, args);
	}


	/**
	 * هوني نحددوا كيفاش الـ Gateway باش تعرف تميز بين مستخدم ومستخدم أخر باش تعمل الـ Rate Limit.
	 * في حالتنا هذي، سنعتمد على الـ IP Address متاع الـ User الخارجي كـ Key.
	 */
	@Bean
	public KeyResolver userKeyResolver() {
		return exchange -> Mono.just(
				exchange.getRequest().getRemoteAddress() != null
						? exchange.getRequest().getRemoteAddress().getAddress().getHostAddress()
						: "anonymous"
		);
	}

}
