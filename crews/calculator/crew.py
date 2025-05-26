from typing import Optional, Dict, Any
from crewai import Agent, Task, Crew, Process
from config.llms import get_llm
from config.settings import VERBOSE_MODE
from ..base_crew import BaseCrew # Import BaseCrew from the parent directory
from tools.calculator_tool import CalculatorTool # Import the new tool

class CalculatorCrew(BaseCrew):
    """
    Crew especializado em realizar cálculos matemáticos básicos.
    """
    description: str = "Crew especializado em realizar cálculos matemáticos básicos."

    def __init__(self, user_input: Optional[str] = None):
        super().__init__(user_input)
        # Initialize the LLM for the crew. 
        # Using gpt-3.5-turbo as it's generally faster and cheaper for focused tasks.
        # Temperature is set low for more deterministic behavior in tool usage.
        self.llm = get_llm(model_name="gpt-3.5-turbo", temperature=0.1)
        self.calculator_agent = None
        self.calculation_task = None

    def _setup_agents_and_tasks(self):
        """
        Configura os agentes e tarefas para o CalculatorCrew.
        Este método é chamado internamente pelo kickoff.
        """
        if not self.user_input:
            # Provide a default or raise an error if user_input is essential
            effective_user_input = "nenhuma expressão fornecida" # Or handle as an error
        else:
            effective_user_input = self.user_input

        self.calculator_agent = Agent(
            role="Calculadora Especialista",
            goal=f"Resolver a expressão matemática fornecida pelo usuário: '{effective_user_input}'. Delegar a tarefa de cálculo para a ferramenta CalculatorTool.",
            backstory="Você é um agente especializado em matemática que usa a CalculatorTool para resolver expressões aritméticas. Você deve passar a expressão exatamente como fornecida para a ferramenta.",
            tools=[CalculatorTool()], # Instantiate the tool
            llm=self.llm,
            verbose=VERBOSE_MODE,
            allow_delegation=False # The agent should use its tool directly
        )

        self.calculation_task = Task(
            description=f"Calcular a seguinte expressão matemática: '{effective_user_input}'. Use a CalculatorTool para obter o resultado. Certifique-se de que a expressão seja passada corretamente para a ferramenta.",
            expected_output="O resultado numérico da expressão como uma string (ex: 'O resultado de ... é X') ou uma mensagem de erro clara se o cálculo não puder ser realizado pela ferramenta.",
            agent=self.calculator_agent
        )

    def kickoff(self) -> Dict[str, Any]:
        """
        Inicia a execução do CalculatorCrew.
        Cria os agentes e tarefas necessários e executa o crew.
        """
        self._setup_agents_and_tasks()

        if not self.calculator_agent or not self.calculation_task:
            return {"status": "error", "message": "Agente de calculadora ou tarefa não configurado corretamente."}

        # Create the Crew for this specific kickoff
        calculator_processing_crew = Crew(
            agents=[self.calculator_agent],
            tasks=[self.calculation_task],
            process=Process.sequential,
            verbose=VERBOSE_MODE
        )

        result = calculator_processing_crew.kickoff()
        # The result from crew.kickoff() is usually the output of the last task.
        # We wrap it in a dictionary as expected by CrewManager.
        return {"result": result}
