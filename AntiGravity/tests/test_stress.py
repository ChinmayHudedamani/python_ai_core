# Copyright (c) 2026 Chinmay Hudedamani. All Rights Reserved.
# APEX AI End-to-End 50-Client Concurrent Double-Booking Stress Test Suite

import sys
import io
import uuid
import asyncio
import unittest
from datetime import date, time
from pathlib import Path

# Force UTF-8 encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.base import Base
from app.models.slot import Slot, SlotStatus
from app.models.patient import Patient
from app.models.booking import Booking, BookingStatus
from app.services.booking_engine import create_booking


class TestConcurrencyStress(unittest.TestCase):

    def test_double_booking_50_concurrent_clients(self):
        print("\n--- ⚡ [STRESS TEST]: 50 Concurrent Clients Booking Same Slot ---")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run_stress():
            # Create a zero-cost local async SQLite engine for stress testing
            stress_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
            async_session_factory = async_sessionmaker(stress_engine, class_=AsyncSession, expire_on_commit=False)

            async with stress_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            # 1. Create a single test slot and 50 patients
            slot_id = uuid.uuid4()
            async with async_session_factory() as session:
                test_slot = Slot(
                    id=slot_id,
                    date=date.today(),
                    time=time(10, 0),
                    doctor_name="Dr. Chinmay Hudedamani",
                    status=SlotStatus.AVAILABLE
                )
                session.add(test_slot)

                patients = []
                for i in range(50):
                    p = Patient(
                        id=uuid.uuid4(),
                        phone_number=f"+9198765{i:05d}",
                        name=f"Stress Patient {i}"
                    )
                    patients.append(p)
                    session.add(p)

                await session.commit()

            # 2. Fire 50 concurrent booking attempts at the exact same millisecond
            async def attempt_booking(p_id: uuid.UUID, client_idx: int):
                async with async_session_factory() as db_session:
                    return await create_booking(
                        db=db_session,
                        patient_id=p_id,
                        slot_id=slot_id,
                        patient_symptoms=f"Stress symptom from patient {client_idx}",
                        procedure_name="Microscopic Single-Sitting Root Canal (RCT)"
                    )

            tasks = [attempt_booking(patients[i].id, i) for i in range(50)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 3. Assertions
            successful_bookings = [r for r in results if isinstance(r, dict) and r.get("success") is True]
            failed_bookings = [r for r in results if isinstance(r, dict) and r.get("success") is False]
            exceptions = [r for r in results if isinstance(r, Exception)]

            if exceptions:
                print(f"DEBUG FIRST EXCEPTION: {repr(exceptions[0])}")

            print(f"📊 Total Concurrent Requests: 50")
            print(f"✅ Successful Bookings: {len(successful_bookings)}")
            print(f"🛑 Safely Rejected Bookings: {len(failed_bookings)}")
            print(f"❌ Unhandled Exceptions: {len(exceptions)}")

            # Assert EXACTLY 1 booking succeeded
            self.assertEqual(len(successful_bookings), 1, "EXACTLY 1 booking must succeed under 50 concurrent requests!")
            # Assert 49 bookings safely rejected
            self.assertEqual(len(failed_bookings), 49, "EXACTLY 49 requests must be safely rejected!")
            # Assert ZERO unhandled exceptions
            self.assertEqual(len(exceptions), 0, "ZERO unhandled exceptions or database deadlocks allowed!")

            await stress_engine.dispose()

        loop.run_until_complete(run_stress())
        loop.close()
        print("🎉 PASSED: 50-Client Concurrency Stress Test completed with 100% data integrity!")


if __name__ == "__main__":
    unittest.main()
