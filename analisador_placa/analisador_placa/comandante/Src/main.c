/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * <h2><center>&copy; Copyright (c) 2019 STMicroelectronics.
  * All rights reserved.</center></h2>
  *
  * This software component is licensed by ST under BSD 3-Clause license,
  * the "License"; You may not use this file except in compliance with the
  * License. You may obtain a copy of the License at:
  *                        opensource.org/licenses/BSD-3-Clause
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "cmsis_os.h"
#include "usb_device.h"
#include "usbd_cdc_if.h"
#define CMD_CO 1
#define CMD_DC 0
#define CMD_ID 2
#define CMD_STAT 3
#define CMD_MOV 4
/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
osThreadId defaultTaskHandle;
osThreadId ouvirHandle;
osThreadId maquinaHandle;
/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
void StartDefaultTask(void const * argument);
void ouvirTask(void const * argument);
void maquina(void const * argument);
void Rodar_Maquina(void);

 static void MX_GPIO_Init(void)
{

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOD_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();

}

// Define States
typedef enum
{
	STATE_DISCONNECTED,
	STATE_STANDBY,
	STATE_MOVING,
	STATE_PAUSED,
	STATE_ERR,
	NUM_STATES
}StateType;

// Function Pointer for State Machines
typedef struct
{
	StateType State;
	void (*func)(void);
}StateMachineType;

// Machine State Prototypes
void Sm_DISCONNECTED(void);
void Sm_STANDBY(void);
void Sm_MOVING(void);
void Sm_PAUSED(void);
void Sm_ERR(void);

StateMachineType StateMachine[] =
{
		{ STATE_DISCONNECTED, Sm_DISCONNECTED },
		{ STATE_STANDBY, Sm_STANDBY },
		{ STATE_PAUSED, Sm_PAUSED},
		{ STATE_MOVING, Sm_MOVING },
		{ STATE_ERR, Sm_ERR },
};

StateType SmState = STATE_DISCONNECTED;

void Sm_DISCONNECTED(void)
{

	 uint8_t temp[10]="ue";
	 uint8_t resposta = 0;
	 uint8_t pergunta_identificador[6] = {"*IDN?"};
	 uint8_t pergunta_conectar[6] = {"*CONN?"};
	 uint8_t resposta_identificador[12] = {"CMDR!"};
	 uint8_t resposta_wtf[12] = {"WTF!!"};
	 uint8_t resposta_conectar[12] = {"OK_CON!"};
	 if( xSemaphoreTake( semafaroUsb ,10000) == pdTRUE )
	 {
	 		  resposta=0;
			  memcpy(temp,buffer_usb,9);
			  osDelay(2);
			  if(memcmp(temp,pergunta_identificador,5)==0 )
				 resposta = CMD_ID;
			  if(memcmp(temp,pergunta_conectar,5)==0 )
				  resposta = CMD_CO;
			  resposta_wtf[4] = memcmp(temp,pergunta_identificador,6) + 48;
			  resposta_wtf[6] = resposta;
			  switch(resposta)
			  {
			  		case CMD_ID:
			  					CDC_Transmit_FS(resposta_identificador,5);
			  					SmState = STATE_DISCONNECTED;
			  					break;
			  		case CMD_CO:
			  					CDC_Transmit_FS(resposta_conectar,5);
			  					SmState = STATE_STANDBY;
			  					break;
			  		default:
			  					CDC_Transmit_FS(resposta_wtf,6);
			  					SmState = STATE_DISCONNECTED;
			}
	}
}
void Sm_STANDBY(void)
{
	 uint8_t temp[10]="ue";
	 uint8_t resposta = 0;
	 uint8_t pergunta_desconectar[6] = {"*DISC"};
	 uint8_t resposta_desconectar[6] = {":( DC"};
	 uint8_t pergunta_status[6] = {"*STAT"};
	 uint8_t resposta_status[6] = {"STBY"};
	 uint8_t pergunta_move[6] = {"*MOVE"};
	 uint8_t resposta_move[6] = {"NO"};
	 uint8_t resposta_wtf[12] = {"WTF!"};
	 if( xSemaphoreTake( semafaroUsb ,10000) == pdTRUE )
	 {
	 		  resposta=-1;
			  memcpy(temp,buffer_usb,9);
			  osDelay(2);
			  if(memcmp(temp,pergunta_status,5)==0 )
				 resposta = CMD_STAT;
			  if(memcmp(temp,pergunta_desconectar,5)==0 )
				  resposta = CMD_DC;
		     if(memcmp(temp,pergunta_move,5)==0 )
				  resposta = CMD_MOV;


			  switch(resposta)
			  {
			  		case CMD_DC:
			  					CDC_Transmit_FS(resposta_desconectar,5);
			  					SmState = STATE_DISCONNECTED;
			  					break;
			  		case CMD_STAT:
			  					CDC_Transmit_FS(resposta_status,5);
			  					SmState = STATE_STANDBY;
			  					break;
			  		case CMD_MOV:
			  					CDC_Transmit_FS(resposta_move,5);
			  					SmState = STATE_STANDBY;
			  					break;
			  		default:
			  					CDC_Transmit_FS(resposta_wtf,5);
			  					SmState = STATE_STANDBY;
			}
	}
}
void Sm_MOVING(void)
{
	SmState = STATE_STANDBY;
}

void Sm_PAUSED(void)
{
	SmState = STATE_MOVING;
}

void Sm_ERR(void)
{
	SmState = STATE_STANDBY;
}

void Rodar_Maquina(void)
{
	if(SmState < NUM_STATES)
	{
		(*StateMachine[SmState].func)();
	}
	else
	{
		return;
	}
}
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */
  

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */


  MX_GPIO_Init();
  /* USER CODE BEGIN 2 */

  /* USER CODE END 2 */

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* definition and creation of defaultTask */
  osThreadDef(defaultTask, StartDefaultTask, osPriorityNormal, 0, 128);
  defaultTaskHandle = osThreadCreate(osThread(defaultTask), NULL);

  osThreadDef(maquinaTask,maquina, osPriorityNormal, 0, 128);
  osThreadDef(ouveTask, ouvirTask, osPriorityNormal, 0, 128);
  maquinaHandle = osThreadCreate(osThread(maquinaTask), NULL);
   ouvirHandle = osThreadCreate(osThread(ouveTask), NULL);

  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

  /* Start scheduler */
  osKernelStart();
  
  /* We should never get here as control is now taken by the scheduler */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the CPU, AHB and APB busses clocks 
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.HSEPredivValue = RCC_HSE_PREDIV_DIV1;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLMUL = RCC_PLL_MUL6;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }
  /** Initializes the CPU, AHB and APB busses clocks 
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_1) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_USB;
  PeriphClkInit.UsbClockSelection = RCC_USBCLKSOURCE_PLL;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */


/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/* USER CODE BEGIN Header_StartDefaultTask */
/**
  * @brief  Function implementing the defaultTask thread.
  * @param  argument: Not used 
  * @retval None
  */
/* USER CODE END Header_StartDefaultTask */


void maquina(void const * argument)
{

	semafaroUsb = xSemaphoreCreateBinary();
	while(1)
	{
		Rodar_Maquina();
	}
}

void ouvirTask(void const * argument)
{

	 // Criar semáfaro binário
	 // Esse semáfaro recebe sinal do callback CDC_Receive_FS
	while(1)
	{
		osDelay(1);
	}
  /* init code for USB_DEVICE */

  /* USER CODE END 5 */
}

void StartDefaultTask(void const * argument)
{
    
    
                 
  /* init code for USB_DEVICE */
  MX_USB_DEVICE_Init();

  /* USER CODE BEGIN 5 */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END 5 */ 
}

/**
  * @brief  Period elapsed callback in non blocking mode
  * @note   This function is called  when TIM4 interrupt took place, inside
  * HAL_TIM_IRQHandler(). It makes a direct call to HAL_IncTick() to increment
  * a global variable "uwTick" used as application time base.
  * @param  htim : TIM handle
  * @retval None
  */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  /* USER CODE BEGIN Callback 0 */

  /* USER CODE END Callback 0 */
  if (htim->Instance == TIM4) {
    HAL_IncTick();
  }
  /* USER CODE BEGIN Callback 1 */

  /* USER CODE END Callback 1 */
}

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */

  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{ 
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     tex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
