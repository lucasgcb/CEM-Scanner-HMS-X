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
#define CMD_MOVX 4
#define CMD_MOVY 5
#define CMD_SSTEP 6
#define CMD_STEPQ 7
/// TODOZAO
/// SEPARAR ESTADOS INTERFACE E ESTADOS ACAO
/// EH ISSO AI MSM
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
void interfaceDuranteMovimento();
void enviarPassos(void);
uint8_t interpretarSerial(uint8_t  *);
uint8_t movimentos_em_x = 0;
uint8_t movimentos_em_y = 0;
uint32_t step_atual = 6969;
typedef struct Comandos
{
	uint8_t conectar[8];
	uint8_t desconectar[8];
	uint8_t moverX[6];
	uint8_t moverY[6];
	uint8_t status[8];
	uint8_t set_step[8];
	uint8_t step[8];
	uint8_t identificar[8];
} Comandos;
typedef struct Respostas
{
	uint8_t conectar[8];
	uint8_t desconectar[8];
	uint8_t moverX[6];
	uint8_t moverY[6];
	uint8_t status[8];
	uint8_t identificar[8];
	uint8_t set_step[8];
	uint8_t step[8];
	uint8_t wtf[8];
} Respostas;

Respostas respostas_disconnected = {"YES_CON",
																  "DISC",
																  "DISC",
																  "DISC",
																  "DISC",
																  "CMDR!",
																  "NCONN",
																  "DISC",
																  "wtf!"};

Respostas respostas_standby = {"ALR_CON",
														 "YES_DIS",
														  "MOVX",
														  "MOVY",
														  "STBY",
														  "CMDR!",
														  "STEP:",
														  "STEP:",
														  "wtf!"};

Respostas respostas_moveX = {"ALR_CON",
														 "YES_DIS",
														  "BUSY",
														  "BUSY",
														  "MOVX",
														  "CMDR!",
														  "BUSY!",
														  "BUSY!",
														  "wtf!"};

Respostas respostas_moveY = {"ALR_CON",
														 "YES_DIS",
														  "BUSY",
														  "BUSY",
														  "MOVY",
														  "CMDR!",
														  "BUSY!",
														  "BUSY!",
														  "wtf!"};


Comandos comandos = {"*CONN?",
											  "*DISC",
											  "*MOVX",
											  "*MOVY",
											  "*STAT?",
											  "*SSTEP",
											  "*STEP?",
											  "*IDN?"};


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
	STATE_MOVINGX,
	STATE_MOVINGY,
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
void Sm_MOVINGX(void);
void Sm_MOVINGY(void);
void Sm_ERR(void);

StateMachineType StateMachine[] =
{
		{ STATE_DISCONNECTED, Sm_DISCONNECTED },
		{ STATE_STANDBY, Sm_STANDBY },
		{ STATE_MOVINGX, Sm_MOVINGX },
		{ STATE_MOVINGY, Sm_MOVINGY },
		{ STATE_ERR, Sm_ERR },
};

StateType SmState = STATE_DISCONNECTED;
void enviarPassos()
{
	char temp[33];
	uint8_t temp2[33];
	uint8_t buff_size = 0;
	for (int i=0; i<33; i++)
	{
			temp2[i]=0;
			temp[i]=0;
	}
	itoa(step_atual,temp,10);
	for (int i=0; i<33; i++)
	{
		    if(temp[i]!=0)
		    {
		    	buff_size++;
		    }
			temp2[i]=temp[i];
	}
	CDC_Transmit_FS(temp2,buff_size);
}

void setPassos(uint8_t* comandoCompleto)
{
	char temp[33];
	uint8_t errstep[9] = {"ERRSTEP",};
	osDelay(1);
	for (int i=0; i<8; i++)
	{
			temp[i]=0;
	}
	for (int i=7; i<16; i++)
	{
			if(comandoCompleto[i]==')')
			{
				temp[i-7] = '\0';
				break;
			}
			if(48 > comandoCompleto[i] || 57< comandoCompleto[i])
			{
				CDC_Transmit_FS(errstep, 8);
				return;
			}

			temp[i-7]=comandoCompleto[i];
	}
	step_atual = atoi(temp);
	enviarPassos();

}
uint8_t interpretarSerial(uint8_t  *entrada)
{
	 if(memcmp(entrada,comandos.identificar,5)==0 )
		 return CMD_ID;
	  if(memcmp(entrada,comandos.conectar,5)==0 )
		 return CMD_CO;
	  if(memcmp(entrada,comandos.desconectar,5)==0 )
		 return CMD_DC;
	  if(memcmp(entrada,comandos.moverX,5)==0 )
		 return CMD_MOVX;
	  if(memcmp(entrada,comandos.moverY,5)==0 )
		 return CMD_MOVY;
	  if(memcmp(entrada,comandos.status,5)==0 )
		 return CMD_STAT;
	  if(memcmp(entrada,comandos.step,5)==0 )
	  	return CMD_STEPQ;
	  if(memcmp(entrada,comandos.set_step,5)==0 )
	  	 return CMD_SSTEP;
	  return -1;
}

void Sm_DISCONNECTED(void)
{

	 uint8_t temp[16]="ue";
	 uint8_t resposta = -1;
	 if( xSemaphoreTake( semafaroUsb ,10000) == pdTRUE )
	 {
		 	 movimentos_em_x = 0;
		 	 movimentos_em_y = 0;
	 		  resposta=-1;
			  memcpy(temp,buffer_usb,16);
			  osDelay(2);
			  resposta = interpretarSerial(temp);

			  switch(resposta)
			  {
			  		case CMD_ID:
			  					CDC_Transmit_FS(respostas_disconnected.identificar ,4);
			  					SmState = STATE_DISCONNECTED;
			  					break;
			  		case CMD_CO:
			  					CDC_Transmit_FS(respostas_disconnected.conectar ,5);
			  					SmState = STATE_STANDBY;
			  					break;
			  		case CMD_DC:
			  					CDC_Transmit_FS(respostas_disconnected.desconectar ,5);
								SmState = STATE_DISCONNECTED;
								break;
			 		case CMD_MOVX:
								CDC_Transmit_FS(respostas_disconnected.moverX ,4);
								SmState = STATE_DISCONNECTED;
								break;
			 		case CMD_MOVY:
								CDC_Transmit_FS(respostas_disconnected.moverY ,4);
								SmState = STATE_DISCONNECTED;
								break;
			 		case CMD_STAT:
								CDC_Transmit_FS(respostas_disconnected.status ,4);
								SmState = STATE_DISCONNECTED;
								break;
			 		case CMD_STEPQ:
								CDC_Transmit_FS(respostas_disconnected.step ,5);
								osDelay(2);
								SmState = STATE_DISCONNECTED;
								break;
			 		case CMD_SSTEP:
								CDC_Transmit_FS(respostas_disconnected.set_step ,5);
								osDelay(2);
								SmState = STATE_DISCONNECTED;
								break;
			  		default:
			  					CDC_Transmit_FS(respostas_disconnected.wtf,4);
			  					SmState = STATE_DISCONNECTED;
			}
	}
}
void Sm_STANDBY(void)
{
	 uint8_t temp[16]="ue";
	 uint8_t resposta = -1;
	 if( xSemaphoreTake( semafaroUsb ,10000) == pdTRUE )
	 {
		      movimentos_em_x = 0;
		 	  movimentos_em_y = 0;
	 		  resposta=-1;
			  memcpy(temp,buffer_usb,15);

			  osDelay(2);
			  resposta = interpretarSerial(temp);

		     switch(resposta)
		   			  {
		   			  		case CMD_ID:
		   			  					CDC_Transmit_FS(respostas_standby.identificar ,5);
		   			  					SmState = STATE_STANDBY;
		   			  					break;
		   			  		case CMD_CO:
		   			  					CDC_Transmit_FS(respostas_standby.conectar ,5);
		   			  					SmState = STATE_STANDBY;
		   			  					break;
		   			  		case CMD_DC:
		   			  					CDC_Transmit_FS(respostas_standby.desconectar ,5);
		   								SmState = STATE_DISCONNECTED;
		   								break;
		   			 		case CMD_MOVX:
		   								CDC_Transmit_FS(respostas_standby.moverX ,4);
										movimentos_em_x = 1 * step_atual;
		   								SmState = STATE_MOVINGX;
		   								break;
		   			 		case CMD_MOVY:
		   								CDC_Transmit_FS(respostas_standby.moverY ,4);
		   								movimentos_em_y = 1 * step_atual;
		   								SmState = STATE_MOVINGY;
		   								break;
		   			 		case CMD_STAT:
		   								CDC_Transmit_FS(respostas_standby.status ,4);
		   								SmState = STATE_STANDBY;
		   								break;
					 		case CMD_STEPQ:
										CDC_Transmit_FS(respostas_standby.step ,5);
										osDelay(2);
										enviarPassos();
										SmState = STATE_STANDBY;
										break;
					 		case CMD_SSTEP:
										CDC_Transmit_FS(respostas_standby.set_step ,5);
										osDelay(2);
										setPassos(temp);
										SmState = STATE_STANDBY;
										break;
		   			  		default:
		   			  					CDC_Transmit_FS(respostas_standby.wtf,4);
		   			  					SmState = STATE_STANDBY;
		   			}
	}
}
void Sm_MOVINGX(void)
{
	uint8_t fim[6] = "MVXOK";
	while(movimentos_em_x>0)
	{
		movimentos_em_x--;
		if (SmState != STATE_MOVINGX)
			return;
		//logica de fazer o bagulho
		osDelay(1);
	}
	CDC_Transmit_FS(fim,5);
	SmState = STATE_STANDBY;
}

void Sm_MOVINGY(void)
{
	uint8_t fim[6] = "MVYOK";
	while(movimentos_em_y>0)
	{
		movimentos_em_y--;
		if (SmState != STATE_MOVINGY)
			return;
		//logica de fazer o bagulho
		osDelay(1);
	}
	CDC_Transmit_FS(fim,5);
	SmState = STATE_STANDBY;
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


void interfaceDuranteMovimento()
{
	uint8_t resposta = -1;
	uint8_t temp[12];
	if ((SmState == STATE_MOVINGX) || (SmState == STATE_MOVINGY))
	{
		 if( xSemaphoreTake( semafaroUsb ,10000) == pdTRUE )
			 {
			 	 	 if ((SmState != STATE_MOVINGX) && (SmState != STATE_MOVINGY))
			 	 	 {
			 	 		xSemaphoreGive( semafaroUsb);
			 	 		return;
			 	 	 }

			 		  resposta=-1;
					  memcpy(temp,buffer_usb,9);

					  osDelay(2);
					  resposta = interpretarSerial(temp);

				     switch(resposta)
				   			  {
				   			  		case CMD_ID:
				   			  					CDC_Transmit_FS(respostas_moveX.identificar ,5);
				   			  					break;
				   			  		case CMD_CO:
				   			  					CDC_Transmit_FS(respostas_moveX.conectar ,5);
				   			  					break;
				   			  		case CMD_DC:
				   			  					CDC_Transmit_FS(respostas_moveX.desconectar ,5);
				   								SmState = STATE_DISCONNECTED;
				   								break;
				   			 		case CMD_MOVX:
				   								CDC_Transmit_FS(respostas_moveX.moverX ,5);
				   								break;
				   			 		case CMD_MOVY:
				   								CDC_Transmit_FS(respostas_moveX.moverY ,5);
				   								break;
				   			 		case CMD_STAT:
		   			 							if (SmState ==  STATE_MOVINGY)
		   			 							{
		   			 								CDC_Transmit_FS(respostas_moveY.status ,5);
		   			 							}
		   			 							if (SmState ==  STATE_MOVINGX)
		   			 							{
		   			 								CDC_Transmit_FS(respostas_moveX.status ,5);
		   			 							}
				   								break;
							 		case CMD_STEPQ:
												CDC_Transmit_FS(respostas_moveX.step ,5);
												osDelay(2);
												break;
							 		case CMD_SSTEP:
												CDC_Transmit_FS(respostas_moveX.set_step ,5);
												osDelay(2);
												break;
				   			  		default:
				   			  					CDC_Transmit_FS(respostas_standby.wtf,4);
				   			}
			}
	}
}

void ouvirTask(void const * argument)
{

	while(1)
	{
		osDelay(1);
		interfaceDuranteMovimento();
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
