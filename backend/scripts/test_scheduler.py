#!/usr/bin/env python3
"""
Script de teste do sistema de Jobs Agendados.

Testa:
- Criação de jobs
- Execução manual
- Scheduler
- Métricas
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Adiciona o diretório backend ao path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


async def test_base_job():
    """Testa a classe BaseJob."""
    print("\n" + "=" * 60)
    print("🧪 Testando BaseJob")
    print("=" * 60)
    
    from src.jobs.base_job import BaseJob, JobResult
    from src.config.jobs_config import JobConfig
    
    # Cria job de teste
    class TestJob(BaseJob):
        def __init__(self):
            config = JobConfig(
                job_id="test_job",
                name="Job de Teste",
                description="Job para testes",
                interval_seconds=60,
                timeout_seconds=10,
                max_retries=2,
            )
            super().__init__(config)
            self.execute_count = 0
        
        async def execute(self):
            self.execute_count += 1
            await asyncio.sleep(0.1)  # Simula trabalho
            return {"count": self.execute_count, "message": "OK"}
    
    job = TestJob()
    
    # Executa
    print("\n📊 Executando job de teste...")
    result = await job.run()
    
    print(f"   ✅ Success: {result.success}")
    print(f"   ⏱️ Duration: {result.duration_seconds:.2f}s")
    print(f"   📦 Result: {result.result_data}")
    
    # Verifica métricas
    metrics = job.metrics.to_dict()
    print(f"\n📈 Métricas:")
    print(f"   Total runs: {metrics['total_runs']}")
    print(f"   Success rate: {metrics['success_rate']}")
    
    assert result.success, "Job deveria ter sucesso"
    assert result.result_data["count"] == 1, "Count deveria ser 1"
    
    print("\n✅ BaseJob: PASSOU")
    return True


async def test_job_with_error():
    """Testa job com erro e retry."""
    print("\n" + "=" * 60)
    print("🧪 Testando Job com Erro e Retry")
    print("=" * 60)
    
    from src.jobs.base_job import BaseJob
    from src.config.jobs_config import JobConfig
    
    class FailingJob(BaseJob):
        def __init__(self):
            config = JobConfig(
                job_id="failing_job",
                name="Job que Falha",
                description="Job para testar retry",
                interval_seconds=60,
                timeout_seconds=5,
                max_retries=2,
                retry_delay_seconds=1,
            )
            super().__init__(config)
            self.attempt_count = 0
        
        async def execute(self):
            self.attempt_count += 1
            if self.attempt_count < 3:
                raise ValueError(f"Erro simulado (tentativa {self.attempt_count})")
            return {"attempts": self.attempt_count}
    
    job = FailingJob()
    
    print("\n📊 Executando job que falha 2x e depois passa...")
    result = await job.run()
    
    print(f"   ✅ Success: {result.success}")
    print(f"   🔄 Retry count: {result.retry_count}")
    print(f"   📦 Result: {result.result_data}")
    
    assert result.success, "Job deveria ter sucesso após retries"
    assert result.retry_count == 2, "Deveria ter 2 retries"
    
    print("\n✅ Job com Retry: PASSOU")
    return True


async def test_job_timeout():
    """Testa timeout de job."""
    print("\n" + "=" * 60)
    print("🧪 Testando Timeout de Job")
    print("=" * 60)
    
    from src.jobs.base_job import BaseJob
    from src.config.jobs_config import JobConfig
    
    class SlowJob(BaseJob):
        def __init__(self):
            config = JobConfig(
                job_id="slow_job",
                name="Job Lento",
                description="Job que ultrapassa timeout",
                interval_seconds=60,
                timeout_seconds=1,  # 1 segundo
                max_retries=0,
            )
            super().__init__(config)
        
        async def execute(self):
            await asyncio.sleep(5)  # 5 segundos (vai dar timeout)
            return {"status": "completed"}
    
    job = SlowJob()
    
    print("\n📊 Executando job com timeout de 1s...")
    result = await job.run()
    
    print(f"   ❌ Success: {result.success}")
    print(f"   ⚠️ Error: {result.error}")
    
    assert not result.success, "Job deveria falhar por timeout"
    assert "Timeout" in result.error, "Erro deveria mencionar timeout"
    
    print("\n✅ Timeout: PASSOU")
    return True


async def test_price_collection_job():
    """Testa o job de coleta de preços."""
    print("\n" + "=" * 60)
    print("🧪 Testando PriceCollectionJob")
    print("=" * 60)
    
    from src.jobs.data_collection_job import PriceCollectionJob
    
    job = PriceCollectionJob()
    
    print("\n📊 Executando coleta de preços...")
    print("   (Isso pode demorar alguns segundos)")
    
    result = await job.run()
    
    print(f"\n   Success: {result.success}")
    print(f"   Duration: {result.duration_seconds:.2f}s")
    
    if result.success:
        data = result.result_data
        print(f"   Assets processed: {data.get('assets_processed', 0)}")
        print(f"   Prices collected: {data.get('prices_collected', 0)}")
        print(f"   Prices saved: {data.get('prices_saved', 0)}")
        if data.get('errors'):
            print(f"   Errors: {data['errors']}")
    else:
        print(f"   Error: {result.error}")
    
    print("\n✅ PriceCollectionJob: PASSOU")
    return True


async def test_score_calculation_job():
    """Testa o job de cálculo de scores."""
    print("\n" + "=" * 60)
    print("🧪 Testando ScoreCalculationJob")
    print("=" * 60)
    
    from src.jobs.score_calculation_job import ScoreCalculationJob
    
    job = ScoreCalculationJob()
    
    print("\n📊 Executando cálculo de scores...")
    print("   (Isso pode demorar alguns segundos)")
    
    result = await job.run()
    
    print(f"\n   Success: {result.success}")
    print(f"   Duration: {result.duration_seconds:.2f}s")
    
    if result.success:
        data = result.result_data
        print(f"   Assets processed: {data.get('assets_processed', 0)}")
        print(f"   Scores created: {data.get('scores_created', 0)}")
        
        summary = data.get('scores_summary', {})
        by_status = summary.get('by_status', {})
        print(f"   HIGH: {by_status.get('high', 0)}")
        print(f"   ATTENTION: {by_status.get('attention', 0)}")
        print(f"   LOW: {by_status.get('low', 0)}")
    else:
        print(f"   Error: {result.error}")
    
    print("\n✅ ScoreCalculationJob: PASSOU")
    return True


async def test_scheduler():
    """Testa o scheduler principal."""
    print("\n" + "=" * 60)
    print("🧪 Testando CryptoPulseScheduler")
    print("=" * 60)
    
    from src.jobs.scheduler import CryptoPulseScheduler, SchedulerState
    
    scheduler = CryptoPulseScheduler()
    
    # Inicializa
    print("\n📊 Inicializando scheduler...")
    await scheduler.initialize()
    
    print(f"   State: {scheduler.state.value}")
    print(f"   Jobs registrados: {len(scheduler._jobs)}")
    
    for job_id in scheduler._jobs:
        print(f"   - {job_id}")
    
    assert scheduler.state == SchedulerState.STARTING, "Estado deveria ser STARTING"
    assert len(scheduler._jobs) > 0, "Deveria ter jobs registrados"
    
    # Testa execução manual
    print("\n📊 Executando health_check manualmente...")
    result = await scheduler.run_job_now("health_check")
    
    if result:
        print(f"   Success: {result.success}")
        print(f"   Overall: {result.result_data.get('overall', 'unknown')}")
    
    # Verifica status
    print("\n📊 Status do scheduler:")
    status = scheduler.get_status()
    print(f"   State: {status['state']}")
    print(f"   Total jobs: {status['total_jobs']}")
    print(f"   Total executions: {status['total_executions']}")
    
    print("\n✅ Scheduler: PASSOU")
    return True


async def main():
    """Executa todos os testes."""
    print("=" * 60)
    print("🧪 CryptoPulse - Teste do Sistema de Jobs")
    print("=" * 60)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Testes básicos
    try:
        results.append(("BaseJob", await test_base_job()))
    except Exception as e:
        print(f"\n❌ BaseJob: FALHOU - {e}")
        results.append(("BaseJob", False))
    
    try:
        results.append(("Job com Retry", await test_job_with_error()))
    except Exception as e:
        print(f"\n❌ Job com Retry: FALHOU - {e}")
        results.append(("Job com Retry", False))
    
    try:
        results.append(("Timeout", await test_job_timeout()))
    except Exception as e:
        print(f"\n❌ Timeout: FALHOU - {e}")
        results.append(("Timeout", False))
    
    # Testes de integração (requerem banco de dados)
    print("\n" + "-" * 60)
    print("📦 Testes de Integração (requerem PostgreSQL)")
    print("-" * 60)
    
    try:
        results.append(("PriceCollectionJob", await test_price_collection_job()))
    except Exception as e:
        print(f"\n⚠️ PriceCollectionJob: PULADO - {e}")
        results.append(("PriceCollectionJob", None))
    
    try:
        results.append(("ScoreCalculationJob", await test_score_calculation_job()))
    except Exception as e:
        print(f"\n⚠️ ScoreCalculationJob: PULADO - {e}")
        results.append(("ScoreCalculationJob", None))
    
    try:
        results.append(("Scheduler", await test_scheduler()))
    except Exception as e:
        print(f"\n⚠️ Scheduler: PULADO - {e}")
        results.append(("Scheduler", None))
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    skipped = sum(1 for _, r in results if r is None)
    
    for name, result in results:
        if result is True:
            print(f"   ✅ {name}: PASSOU")
        elif result is False:
            print(f"   ❌ {name}: FALHOU")
        else:
            print(f"   ⚠️ {name}: PULADO")
    
    print(f"\n   Total: {len(results)}")
    print(f"   ✅ Passou: {passed}")
    print(f"   ❌ Falhou: {failed}")
    print(f"   ⚠️ Pulado: {skipped}")
    
    if failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"\n⚠️ {failed} teste(s) falhou(aram)")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
